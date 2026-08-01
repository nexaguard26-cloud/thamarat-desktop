/**
 * Thamarat ERP Desktop - Electron Main Process
 */

const { app, BrowserWindow, Menu, Tray, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let backendProcess;
let tray;

// Get user data path
const userDataPath = app.getPath('userData');
const backendPath = path.join(__dirname, '..', 'backend');
const logsPath = path.join(userDataPath, 'logs');
const dbPath = path.join(userDataPath, 'thamarat.db');

// Ensure directories exist
[logsPath, userDataPath].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    const logFile = path.join(logsPath, `thamarat-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, logMessage);
    console.log(logMessage);
}

function startBackend() {
    log('Starting backend server...');
    
    // Check if Python is available
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    backendProcess = spawn(pythonCmd, ['main.py'], {
        cwd: backendPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });
    
    backendProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        log(`Backend: ${output}`);
        
        // Check if server started successfully
        if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
            log('Backend server started successfully');
        }
    });
    
    backendProcess.stderr.on('data', (data) => {
        log(`Backend Error: ${data.toString().trim()}`);
    });
    
    backendProcess.on('error', (error) => {
        log(`Backend process error: ${error.message}`);
    });
    
    backendProcess.on('exit', (code) => {
        log(`Backend exited with code ${code}`);
        if (code !== 0) {
            setTimeout(startBackend, 5000); // Retry after 5 seconds
        }
    });
}

function createWindow() {
    log('Creating main window...');
    
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 700,
        title: 'Thamarat ERP - نظام المحاسبة',
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    });
    
    // Load the frontend
    const frontendPath = path.join(__dirname, '..', 'frontend', 'build');
    if (fs.existsSync(frontendPath)) {
        mainWindow.loadFile(path.join(frontendPath, 'index.html'));
    } else {
        // Development mode - load from dev server
        mainWindow.loadURL('http://localhost:3000');
    }
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        log('Main window displayed');
    });
    
    // Handle window close
    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            return false;
        }
    });
    
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function createTray() {
    const iconPath = path.join(__dirname, 'tray-icon.png');
    
    // Create a simple tray icon if it doesn't exist
    if (!fs.existsSync(iconPath)) {
        log('Tray icon not found, using default');
    }
    
    tray = new Tray(iconPath);
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'فتح Thamarat',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                }
            }
        },
        {
            label: 'نسخ احتياطي',
            click: () => {
                createBackup();
            }
        },
        { type: 'separator' },
        {
            label: 'الخروج',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);
    
    tray.setToolTip('Thamarat ERP');
    tray.setContextMenu(contextMenu);
    
    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
        }
    });
}

function createBackup() {
    const backupDir = path.join(userDataPath, 'backups');
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(backupDir, `thamarat-backup-${timestamp}.db`);
    
    if (fs.existsSync(dbPath)) {
        fs.copyFileSync(dbPath, backupPath);
        dialog.showMessageBox({
            type: 'info',
            title: 'نسخ احتياطي',
            message: `تم إنشاء نسخة احتياطية بنجاح\n${backupPath}`
        });
        log(`Backup created: ${backupPath}`);
    }
}

function createMenu() {
    const template = [
        {
            label: 'ملف',
            submenu: [
                {
                    label: 'نسخ احتياطي',
                    accelerator: 'CmdOrCtrl+B',
                    click: () => createBackup()
                },
                {
                    label: 'استيراد بيانات',
                    accelerator: 'CmdOrCtrl+I',
                    click: () => {
                        dialog.showOpenDialog(mainWindow, {
                            properties: ['openFile'],
                            filters: [{ name: 'Database', extensions: ['db', 'sqlite'] }]
                        }).then(result => {
                            if (!result.canceled && result.filePaths.length > 0) {
                                // Import logic here
                            }
                        });
                    }
                },
                { type: 'separator' },
                {
                    label: 'الخروج',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        app.isQuitting = true;
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'تحرير',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                { role: 'selectAll' }
            ]
        },
        {
            label: 'عرض',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'مساعدة',
            submenu: [
                {
                    label: 'عن Thamarat',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'عن Thamarat ERP',
                            message: 'Thamarat ERP v1.0.0',
                            detail: 'نظام محاسبة المنظمات الإنسانية\nHumanitarian Accounting System\n\n© 2026 NexaGuard_Ye AI Solutions'
                        });
                    }
                },
                {
                    label: 'فتح مجلد البيانات',
                    click: () => {
                        shell.openPath(userDataPath);
                    }
                }
            ]
        }
    ];
    
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// IPC Handlers
ipcMain.handle('get-app-info', () => {
    return {
        version: app.getVersion(),
        userDataPath: userDataPath,
        dbPath: dbPath
    };
});

ipcMain.handle('create-backup', () => {
    createBackup();
    return { success: true };
});

ipcMain.handle('open-external', (event, url) => {
    shell.openExternal(url);
});

// App lifecycle
app.whenReady().then(() => {
    log('App ready, initializing...');
    
    createMenu();
    startBackend();
    createWindow();
    createTray();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    log('App quitting...');
    app.isQuitting = true;
    
    // Stop backend
    if (backendProcess) {
        backendProcess.kill();
    }
});

log('Thamarat ERP Desktop starting...');
