import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Space, Typography, Switch, Select, message, Modal, Descriptions, Divider } from 'antd';
import { GlobalOutlined, DatabaseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [form] = Form.useForm();
  const [licenseInfo, setLicenseInfo] = useState<any>(null);

  useEffect(() => {
    fetchLicenseInfo();
  }, []);

  const fetchLicenseInfo = async () => {
    setLicenseInfo({
      type: 'trial',
      days_remaining: 25,
      organization: null,
    });
  };

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('i18nextLng', lang);
  };

  const handleBackup = () => {
    if (window.electronAPI) {
      window.electronAPI.createBackup();
      message.success(t('common.success'));
    } else {
      message.info('Backup functionality available in desktop app');
    }
  };

  const showLicenseActivation = () => {
    Modal.confirm({
      title: 'تفعيل الترخيص',
      content: (
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Input placeholder="مفتاح الترخيص" />
          <Input placeholder="اسم المؤسسة" />
        </Space>
      ),
      onOk: () => {
        message.success('تم تفعيل الترخيص بنجاح');
      },
    });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={3}>{t('settings.title')}</Title>

      <Card title={<><GlobalOutlined /> {t('settings.general')}</>}>
        <Form layout="vertical">
          <Form.Item label={t('settings.language')}>
            <Select
              value={i18n.language}
              onChange={handleLanguageChange}
              style={{ width: 200 }}
            >
              <Select.Option value="ar">العربية</Select.Option>
              <Select.Option value="en">English</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Card>

      <Card title={<><DatabaseOutlined /> {t('settings.backup')}</>}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Button type="primary" onClick={handleBackup}>
            {t('settings.backupNow')}
          </Button>
          <Text type="secondary">
            سيتم إنشاء نسخة احتياطية في مجلد بيانات التطبيق
          </Text>
        </Space>
      </Card>

      <Card title={<><InfoCircleOutlined /> {t('settings.about')}</>}>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="اسم المنتج">Thamarat ERP</Descriptions.Item>
          <Descriptions.Item label="الإصدار">1.0.0</Descriptions.Item>
          <Descriptions.Item label="الترخيص">
            <Space>
              <Text type={licenseInfo?.type === 'trial' ? 'warning' : 'success'}>
                {licenseInfo?.type === 'trial' ? 'تجريبي' : 'مفعل'}
              </Text>
              {licenseInfo?.type === 'trial' && (
                <Text type="secondary">
                  ({licenseInfo?.days_remaining} يوم متبقي)
                </Text>
              )}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="المؤسسة">
            {licenseInfo?.organization || 'غير محدد'}
          </Descriptions.Item>
        </Descriptions>
        
        {licenseInfo?.type === 'trial' && (
          <>
            <Divider />
            <Button type="primary" onClick={showLicenseActivation}>
              تفعيل الترخيص التجاري
            </Button>
          </>
        )}
      </Card>

      <Card>
        <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
          © 2026 NexaGuard_Ye AI Solutions
        </Text>
        <Text type="secondary" style={{ textAlign: 'center', display: 'block' }}>
          نظام محاسبة المنظمات الإنسانية
        </Text>
      </Card>
    </Space>
  );
};

export default Settings;
