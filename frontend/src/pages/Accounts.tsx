import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Tree, Card, message } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title } = Typography;

interface Account {
  id: string;
  code: string;
  name_ar: string;
  name_en?: string;
  account_type_name?: string;
  balance: number;
  level: number;
  children?: Account[];
}

const Accounts: React.FC = () => {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/accounts', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAccounts(response.data);
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
      title: t('accounts.accountCode'),
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: t('accounts.accountName'),
      dataIndex: 'name_ar',
      key: 'name_ar',
    },
    {
      title: t('accounts.accountType'),
      dataIndex: 'account_type_name',
      key: 'account_type_name',
      width: 150,
    },
    {
      title: t('accounts.balance'),
      dataIndex: 'balance',
      key: 'balance',
      width: 150,
      render: (balance: number) => (
        <span style={{ fontWeight: 500, color: balance < 0 ? '#ff4d4f' : '#52c41a' }}>
          {formatCurrency(balance)}
        </span>
      ),
    },
    {
      title: '',
      key: 'actions',
      width: 100,
      render: () => (
        <Button type="link" icon={<EditOutlined />} />
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3}>{t('accounts.title')}</Title>
        <Button type="primary" icon={<PlusOutlined />}>
          {t('accounts.addAccount')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 50 }}
          expandable={{
            defaultExpandAllRows: true,
          }}
        />
      </Card>
    </Space>
  );
};

export default Accounts;
