import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import ptBR from 'antd/locale/pt_BR'
import App from './App'
import './styles/global.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={ptBR} theme={{ token: { colorPrimary: '#166534' } }}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>,
)
