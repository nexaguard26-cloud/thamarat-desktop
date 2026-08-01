import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Card, Tag, Progress, message, Modal, Form, Input, InputNumber, Select } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title } = Typography;

const Funds: React.FC = () => {
  const { t } = useTranslation();
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchFunds();
  }, []);

  const fetchFunds = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/funds', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFunds(response.data);
    } catch (error) {
      message.error(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ar-YE', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const columns = [
    {
      title: t('funds.fundNumber'),
      dataIndex: 'fund_number',
      key: 'fund_number',
      width: 120,
    },
    {
      title: t('funds.fundName'),
      dataIndex: 'name_ar',
      key: 'name_ar',
    },
    {
      title: t('funds.donor'),
      dataIndex: 'donor_name',
      key: 'donor_name',
    },
    {
      title: t('funds.fundType'),
      dataIndex: 'fund_type',
      key: 'fund_type',
      render: (type: string) => <Tag color="blue">{t(`funds.${type}`)}</Tag>,
    },
    {
      title: t('funds.totalAmount'),
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 150,
      render: (val: number) => formatCurrency(val),
    },
    {
      title: t('funds.utilizationRate'),
      dataIndex: 'utilization_rate',
      key: 'utilization_rate',
      width: 150,
      render: (rate: number) => (
        <Progress percent={Math.min(rate, 100)} size="small" />
      ),
    },
    {
      title: t('funds.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'default'}>
          {t(`funds.${status}`)}
        </Tag>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3}>{t('funds.title')}</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
          {t('funds.addFund')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={funds}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>

      <Modal
        title={t('funds.addFund')}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={600}
      >
        <Form layout="vertical">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Space>
              <Form.Item label={t('funds.fundNumber')} name="fund_number" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item label={t('funds.fundType')} name="fund_type" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="unrestricted">{t('funds.unrestricted')}</Select.Option>
                  <Select.Option value="restricted">{t('funds.restricted')}</Select.Option>
                  <Select.Option value="temporarily_restricted">{t('funds.temporarilyRestricted')}</Select.Option>
                </Select>
              </Form.Item>
            </Space>
            <Form.Item label={t('funds.fundName')} name="name_ar" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item label={t('funds.totalAmount')} name="total_amount" rules={[{ required: true }]}>
              <InputNumber style={{ width: '100%' }} />
            </Form.Item>
            <Button type="primary" htmlType="submit">{t('common.save')}</Button>
          </Space>
        </Form>
      </Modal>
    </Space>
  );
};

export default Funds;
