import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', 
        new URLSearchParams({
          username: values.email,
          password: values.password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      message.success(t('common.success'));
      navigate('/dashboard');
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('auth.invalidCredentials'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          borderRadius: 16,
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
        }}
        styles={{ body: { padding: 40 } }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8, color: '#1890ff' }}>
              ثمرة ERP
            </Title>
            <Text type="secondary">{t('auth.loginSubtitle')}</Text>
          </div>

          <Form
            name="login"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: t('auth.email') + ' مطلوب' },
                { type: 'email', message: 'البريد الإلكتروني غير صحيح' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder={t('auth.email')}
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: t('auth.password') + ' مطلوب' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder={t('auth.password')}
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                {t('auth.login')}
              </Button>
            </Form.Item>
          </Form>

          <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
            © 2026 NexaGuard_Ye AI Solutions
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default Login;
