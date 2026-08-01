import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Card, Tag, DatePicker, Select, message, Modal, Form, Input, InputNumber } from 'antd';
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import dayjs from 'dayjs';

const { Title } = Typography;
const { RangePicker } = DatePicker;

const JournalEntries: React.FC = () => {
  const { t } = useTranslation();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/journal', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEntries(response.data);
    } catch (error) {
      message.error(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handlePost = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:5000/api/journal/${id}/post`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      message.success(t('common.success'));
      fetchEntries();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('common.error'));
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
      title: t('journal.entryNumber'),
      dataIndex: 'entry_number',
      key: 'entry_number',
      width: 150,
    },
    {
      title: t('journal.entryDate'),
      dataIndex: 'entry_date',
      key: 'entry_date',
      width: 120,
    },
    {
      title: t('journal.description'),
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: t('journal.totalDebit'),
      dataIndex: 'total_debit',
      key: 'total_debit',
      width: 150,
      render: (val: number) => formatCurrency(val),
    },
    {
      title: t('journal.totalCredit'),
      dataIndex: 'total_credit',
      key: 'total_credit',
      width: 150,
      render: (val: number) => formatCurrency(val),
    },
    {
      title: t('journal.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colors: Record<string, string> = {
          draft: 'default',
          posted: 'success',
          reversed: 'error',
        };
        return <Tag color={colors[status]}>{t(`journal.${status}`)}</Tag>;
      },
    },
    {
      title: '',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          {record.status === 'draft' && (
            <Button
              type="link"
              icon={<CheckOutlined />}
              onClick={() => handlePost(record.id)}
            >
              {t('journal.post')}
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3}>{t('journal.title')}</Title>
        <Space>
          <RangePicker />
          <Select placeholder={t('journal.status')} style={{ width: 120 }} allowClear>
            <Select.Option value="draft">{t('journal.draft')}</Select.Option>
            <Select.Option value="posted">{t('journal.posted')}</Select.Option>
          </Select>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            {t('journal.newEntry')}
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={entries}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>

      <Modal
        title={t('journal.newEntry')}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={800}
      >
        <Form layout="vertical">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Space>
              <Form.Item label={t('journal.entryDate')} name="entry_date">
                <DatePicker />
              </Form.Item>
              <Form.Item label={t('journal.reference')} name="reference">
                <Input />
              </Form.Item>
            </Space>
            <Form.Item label={t('journal.description')} name="description">
              <Input.TextArea rows={2} />
            </Form.Item>
            <Button type="primary">{t('common.save')}</Button>
          </Space>
        </Form>
      </Modal>
    </Space>
  );
};

export default JournalEntries;
