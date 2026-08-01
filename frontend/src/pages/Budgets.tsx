import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Card, Tag, Progress, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title } = Typography;

const Budgets: React.FC = () => {
  const { t } = useTranslation();
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/budgets', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setBudgets(response.data);
    } catch (error) {
      message.error(t('common.error'));
    } finally {
      setLoading(false);
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
    {
      title: t('budgets.budgetYear'),
      dataIndex: 'fiscal_year',
      key: 'fiscal_year',
      width: 120,
    },
    {
      title: 'رقم الميزانية',
      dataIndex: 'budget_number',
      key: 'budget_number',
    },
    {
      title: t('budgets.totalBudget'),
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 150,
      render: (val: number) => formatCurrency(val),
    },
    {
      title: 'المصروف',
      dataIndex: 'total_actual',
      key: 'total_actual',
      width: 150,
      render: (val: number) => formatCurrency(val),
    },
    {
      title: 'نسبة الإنفاق',
      key: 'utilization',
      width: 150,
      render: (_: any, record: any) => {
        const rate = record.total_amount > 0 ? (record.total_actual / record.total_amount) * 100 : 0;
        return <Progress percent={Math.min(rate, 100)} size="small" />;
      },
    },
    {
      title: t('budgets.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'approved' ? 'success' : 'default'}>
          {t(`budgets.${status}`)}
        </Tag>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3}>{t('budgets.title')}</Title>
        <Button type="primary" icon={<PlusOutlined />}>
          {t('budgets.addBudget')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={budgets}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </Space>
  );
};

export default Budgets;
