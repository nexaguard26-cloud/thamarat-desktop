import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Progress, Typography, Space } from 'antd';
import {
  BankOutlined,
  WalletOutlined,
  RiseOutlined,
  FallOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title } = Typography;

interface DashboardData {
  totalAssets: number;
  totalLiabilities: number;
  totalEquity: number;
  recentEntries: any[];
  funds: any[];
}

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData>({
    totalAssets: 0,
    totalLiabilities: 0,
    totalEquity: 0,
    recentEntries: [],
    funds: [],
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const today = new Date().toISOString().split('T')[0];
      
      // Fetch balance sheet
      const balanceSheetRes = await axios.get(
        `http://localhost:5000/api/reports/balance-sheet?as_of_date=${today}`,
        { headers }
      );
      
      setData({
        totalAssets: balanceSheetRes.data.totals.total_assets || 0,
        totalLiabilities: balanceSheetRes.data.totals.total_liabilities || 0,
        totalEquity: balanceSheetRes.data.totals.total_equity || 0,
        recentEntries: [],
        funds: [],
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ar-YE', {
      style: 'currency',
      currency: 'YER',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const columns = [
    { title: t('journal.entryNumber'), dataIndex: 'entry_number', key: 'entry_number' },
    { title: t('journal.entryDate'), dataIndex: 'entry_date', key: 'entry_date' },
    { title: t('journal.description'), dataIndex: 'description', key: 'description' },
    { 
      title: t('journal.status'), 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          draft: { color: 'default', text: t('journal.draft') },
          posted: { color: 'success', text: t('journal.posted') },
          reversed: { color: 'error', text: t('journal.reversed') },
        };
        const s = statusMap[status] || statusMap.draft;
        return <span style={{ color: s.color }}>{s.text}</span>;
      }
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={3}>{t('dashboard.title')}</Title>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('dashboard.totalAssets')}
              value={data.totalAssets}
              formatter={(value) => formatCurrency(Number(value))}
              prefix={<BankOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('dashboard.totalLiabilities')}
              value={data.totalLiabilities}
              formatter={(value) => formatCurrency(Number(value))}
              prefix={<FallOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('dashboard.totalEquity')}
              value={data.totalEquity}
              formatter={(value) => formatCurrency(Number(value))}
              prefix={<RiseOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('funds.title')}
              value={data.funds.length}
              prefix={<WalletOutlined />}
              suffix={t('funds.title')}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title={t('dashboard.recentEntries')} extra={<FileTextOutlined />}>
            <Table
              columns={columns}
              dataSource={data.recentEntries}
              rowKey="id"
              size="small"
              pagination={false}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title={t('dashboard.fundUtilization')}>
            {data.funds.slice(0, 5).map((fund) => (
              <div key={fund.id} style={{ marginBottom: 16 }}>
                <Space>
                  <span>{fund.name_ar}</span>
                  <span type="secondary">{fund.fund_number}</span>
                </Space>
                <Progress
                  percent={Math.min(fund.utilization_rate || 0, 100)}
                  status={fund.utilization_rate > 90 ? 'exception' : 'normal'}
                  strokeColor={fund.utilization_rate > 90 ? '#ff4d4f' : '#1890ff'}
                />
              </div>
            ))}
            {data.funds.length === 0 && (
              <div style={{ textAlign: 'center', color: '#999' }}>
                {t('common.noData')}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </Space>
  );
};

export default Dashboard;
