import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Layout as AntLayout, Menu, theme, Dropdown, Avatar, Space, Typography } from 'antd';
import {
  DashboardOutlined,
  BankOutlined,
  FileTextOutlined,
  WalletOutlined,
  BarChartOutlined,
  PieChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

const Layout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: t('menu.dashboard') },
    { key: '/accounts', icon: <BankOutlined />, label: t('menu.accounts') },
    { key: '/journal', icon: <FileTextOutlined />, label: t('menu.journal') },
    { key: '/funds', icon: <WalletOutlined />, label: t('menu.funds') },
    { key: '/budgets', icon: <BarChartOutlined />, label: t('menu.budgets') },
    { key: '/reports', icon: <PieChartOutlined />, label: t('menu.reports') },
    { key: '/settings', icon: <SettingOutlined />, label: t('menu.settings') },
  ];

  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
    localStorage.setItem('i18nextLng', newLang);
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('menu.settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('menu.logout'),
      onClick: () => {
        localStorage.removeItem('token');
        navigate('/login');
      },
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        theme="light"
        breakpoint="lg"
        collapsedWidth="0"
        style={{ borderInlineEnd: '1px solid #f0f0f0' }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 20,
            fontWeight: 'bold',
            color: '#1890ff',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          ثمرة ERP
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['/dashboard']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ height: 'calc(100vh - 64px)', borderInlineEnd: 0 }}
        />
      </Sider>
      <AntLayout>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Space size="middle">
            <GlobalOutlined
              style={{ fontSize: 18, cursor: 'pointer' }}
              onClick={toggleLanguage}
              title={i18n.language === 'ar' ? 'English' : 'العربية'}
            />
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <Text>المستخدم</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
