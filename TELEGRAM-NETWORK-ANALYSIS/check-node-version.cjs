#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkNodeVersion() {
    log('\n==================================================', 'cyan');
    log('Node.js Version Checker', 'cyan');
    log('==================================================\n', 'cyan');

    // Read .nvmrc
    const nvmrcPath = path.join(process.cwd(), '.nvmrc');

    if (!fs.existsSync(nvmrcPath)) {
        log('[ERROR] .nvmrc file not found', 'red');
        log('Please create a .nvmrc file in your project root\n', 'yellow');
        process.exit(1);
    }

    const requiredVersion = fs.readFileSync(nvmrcPath, 'utf8').trim();
    const currentVersion = process.version.slice(1); // Remove 'v' prefix

    log(`Required version: ${requiredVersion}`, 'green');
    log(`Current version:  ${currentVersion}`, 'green');

    // Parse versions
    const required = requiredVersion.split('.').map(Number);
    const current = currentVersion.split('.').map(Number);

    // Compare major version
    if (current[0] !== required[0]) {
        log('\n[ERROR] Node.js major version mismatch!', 'red');
        log(`Expected: ${requiredVersion}`, 'yellow');
        log(`Current:  ${currentVersion}`, 'yellow');
        log('\nPlease run: nvm use ' + requiredVersion, 'cyan');
        log('Or run: .\\setup-node.bat (Windows)\n', 'cyan');
        process.exit(1);
    }

    // Compare minor version (warning only)
    if (current[1] !== required[1]) {
        log('\n[WARN] Node.js minor version mismatch', 'yellow');
        log(`Expected: ${requiredVersion}`, 'yellow');
        log(`Current:  ${currentVersion}`, 'yellow');
        log('Consider updating to match the required version\n', 'cyan');
    }

    log('\n[SUCCESS] Node.js version is compatible!\n', 'green');
}

checkNodeVersion();