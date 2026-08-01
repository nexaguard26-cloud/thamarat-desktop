import React, { useState } from 'react';
import { Card, Row, Col, Button, DatePicker, Space, Typography, Table, message } from 'antd';
import { FileTextOutlined, DownloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const Reports: React.FC = () => {
  const { t } = useTranslation();
  const [reportType, setReportType] = useState<string | null>(null);
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<any>([dayjs().startOf('year'), dayjs()]);
  const [asOfDate, setAsOfDate] = useState(dayjs());

  const reportTypes = [
    { key: 'balance_sheet', title: t('reports.balanceSheet'), icon: '📊' },
    { key: 'income_statement', title: t('reports.incomeStatement'), icon: '📈' },
    { key: 'trial_balance', title: t('journal.trialBalance'), icon: '⚖️' },
  ];

  const generateReport = async () => {
    if (!reportType) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      let response;
      if (reportType === 'balance_sheet') {
        response = await axios.get(
          `http://localhost:5000/api/reports/balance-sheet?as_of_date=${asOfDate.format('YYYY-MM-DD')}`,
          { headers }
        );
        setReportData(response.data);
      } else if (reportType === 'income_statement') {
        response = await axios.get(
          `http://localhost:5000/api/reports/income-statement?start_date=${dateRange[0].format('YYYY-MM-DD')}&end_date=${dateRange[1].format('YYYY-MM-DD')}`,
          { headers }
        );
        setReportData(response.data);
      } else if (reportType === 'trial_balance') {
        response = await axios.get(
          `http://localhost:5000/api/reports/trial-balance?as_of_date=${asOfDate.format('YYYY-MM-DD')}`,
          { headers }
        );
        setReportData(response.data);
      }
    } catch (error) {
      message.error(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const renderReport = () => {
    if (!reportData) return null;

    if (reportType === 'balance_sheet') {
      return (
        <Card title={t('reports.balanceSheet')}>
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Title level={4}>الأصول</Title>
              {reportData.assets?.items?.map((item: any) => (
                <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Text>{item.name}</Text>
                  <Text strong>{item.balance.toLocaleString()}</Text>
                </div>
              ))}
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', fontWeight: 'bold' }}>
                <Text strong>إجمالي الأصول</Text>
                <Text strong>{reportData.assets?.total?.toLocaleString()}</Text>
              </div>
            </Col>
            <Col span={12}>
              <Title level={4}>الخصوم وحقوق الملكية</Title>
              {reportData.liabilities?.items?.map((item: any) => (
                <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Text>{item.name}</Text>
                  <Text strong>{item.balance.toLocaleString()}</Text>
                </div>
              ))}
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text>إجمالي الخصوم</Text>
                <Text strong>{reportData.liabilities?.total?.toLocaleString()}</Text>
              </div>
              {reportData.equity?.items?.map((item: any) => (
                <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <Text>{item.name}</Text>
                  <Text strong>{item.balance.toLocaleString()}</Text>
                </div>
              ))}
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', fontWeight: 'bold' }}>
                <Text strong>إجمالي الخصوم وحقوق الملكية</Text>
                <Text strong>{(reportData.liabilities?.total + reportData.equity?.total)?.toLocaleString()}</Text>
              </div>
            </Col>
          </Row>
        </Card>
      );
    }

    if (reportType === 'income_statement') {
      return (
        <Card title={t('reports.incomeStatement')}>
          <Title level={4}>الإيرادات</Title>
          {reportData.revenues?.items?.map((item: any) => (
            <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>{item.name}</Text>
              <Text strong>{item.amount.toLocaleString()}</Text>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', fontWeight: 'bold' }}>
            <Text strong>إجمالي الإيرادات</Text>
            <Text strong>{reportData.revenues?.total?.toLocaleString()}</Text>
          </div>
          
          <Title level={4} style={{ marginTop: 24 }}>المصروفات</Title>
          {reportData.expenses?.items?.map((item: any) => (
            <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
              <Text>{item.name}</Text>
              <Text strong>{item.amount.toLocaleString()}</Text>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', fontWeight: 'bold' }}>
            <Text strong>إجمالي المصروفات</Text>
            <Text strong>{reportData.expenses?.total?.toLocaleString()}</Text>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 0', fontWeight: 'bold', fontSize: 18, borderTop: '2px solid #1890ff' }}>
            <Text strong>صافي الفائض/العجز</Text>
            <Text strong style={{ color: reportData.result?.net_surplus >= 0 ? '#52c41a' : '#ff4d4f' }}>
              {reportData.result?.net_surplus?.toLocaleString()}
            </Text>
          </div>
        </Card>
      );
    }

    return null;
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={3}>{t('reports.title')}</Title>
      
      <Row gutter={[16, 16]}>
        {reportTypes.map((report) => (
          <Col xs={24} sm={8} key={report.key}>
            <Card
              hoverable
              onClick={() => {
                setReportType(report.key);
                setReportData(null);
              }}
              style={{
                borderColor: reportType === report.key ? '#1890ff' : undefined,
                background: reportType === report.key ? '#e6f7ff' : undefined,
              }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text style={{ fontSize: 32 }}>{report.icon}</Text>
                <Text strong>{report.title}</Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {reportType && (
        <Card>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Space>
              {reportType === 'income_statement' ? (
                <RangePicker value={dateRange} onChange={(dates) => dates && setDateRange(dates)} />
              ) : (
                <DatePicker value={asOfDate} onChange={(date) => date && setAsOfDate(date)} />
              )}
              <Button type="primary" icon={<FileTextOutlined />} onClick={generateReport} loading={loading}>
                {t('reports.generateReport')}
              </Button>
              <Button icon={<DownloadOutlined />}>{t('common.export')}</Button>
            </Space>

            {renderReport()}
          </Space>
        </Card>
      )}
    </Space>
  );
};

export default Reports;
