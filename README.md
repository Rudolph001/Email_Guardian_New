# Email Guardian - Local Installation

Email Guardian is a comprehensive email security analysis platform that helps detect threats, analyze communication patterns, and manage email security risks.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation

1. **Download Files**
   - Download `setup.py` and `local_standalone.py` to a folder
   - Open terminal/command prompt in that folder

2. **Run Setup**
   ```bash
   python setup.py
   ```

3. **Start Application**
   ```bash
   python local_standalone.py
   ```

4. **Access Web Interface**
   - Open browser to: http://127.0.0.1:5000

## Features

- **CSV File Processing**: Upload and analyze Tessian email export files
- **Risk Analysis**: Machine learning-based threat detection
- **Domain Management**: Automatic domain classification and whitelisting
- **Case Management**: Track and investigate security incidents
- **Interactive Dashboards**: Real-time analytics and visualizations
- **Business Rules**: Configurable filtering and escalation rules

## System Requirements

- **Python**: 3.8+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for application, additional space for data files
- **Browser**: Chrome, Firefox, Safari, or Edge

## File Structure

```
email-guardian/
├── setup.py                 # Installation script
├── local_standalone.py      # Main application
├── requirements.txt         # Python dependencies
├── uploads/                 # CSV file uploads
├── data/                    # Session data storage
└── local_email_guardian.db  # SQLite database
```

## Troubleshooting

### Installation Issues
- **Python not found**: Install Python from python.org
- **Package installation fails**: Try `pip install --user package_name`
- **Permission errors**: Run as administrator (Windows) or use `sudo` (Mac/Linux)

### Runtime Issues
- **Port 5000 in use**: Change port in local_standalone.py
- **Database errors**: Delete `local_email_guardian.db` and restart
- **Import errors**: Run `python setup.py` again

### Performance
- **Large files**: Process files in smaller chunks
- **Memory issues**: Close other applications, increase available RAM
- **Slow analysis**: Use SSD storage for better performance

## Data Privacy

- All data processing happens locally on your machine
- No data is sent to external servers
- CSV files and analysis results stored locally
- Database can be encrypted using SQLite encryption extensions

## Support

For issues with the local installation:
1. Check system requirements
2. Verify Python version compatibility
3. Ensure all dependencies are installed
4. Review console output for error messages

## License

This software is provided for local use and analysis purposes.