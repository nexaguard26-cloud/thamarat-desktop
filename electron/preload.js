/**
 * Electron Preload Script
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
    // App info
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    
    // Backup
    createBackup: () => ipcRenderer.invoke('create-backup'),
    
    // External links
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Platform info
    platform: process.platform,
    
    // Check if running in Electron
    isDesktop: true
});

// Log that preload is ready
console.log('Thamarat ERP Desktop - Preload script loaded');
