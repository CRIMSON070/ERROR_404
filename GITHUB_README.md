# 🏏 IPL 2025 Auction Dashboard - Hadoop/Spark Integration

Professional IPL Auction Strategy Dashboard with real-time analytics, built using Hadoop and Apache Spark for big data processing.

## 🚀 Features

- **622 Real Players**: All players from ipl_2025_auction_players.csv with proper names and team affiliations
- **Hadoop/Spark Processing**: Big data pipeline for player analytics
- **120 Crore Budget Management**: Enhanced budget system for team building
- **Multi-criteria Filtering**: Search by name, team, role, and budget range
- **Real-time Analytics**: Live performance tracking and team balance assessment
- **Color-coded Budget Categories**: ₹15+ Cr, ₹10-15 Cr, ₹5-10 Cr, ₹2-5 Cr, ₹0-2 Cr
- **Professional Dark Theme UI**: IPL-branded interface with gradients
- **Team Building Interface**: Drag-and-drop player selection with slot management

## 📁 Project Structure

```
IPL_BIG_DATA_PROJECT/
├── final_hadoop_spark_dashboard.html    # Main dashboard
├── dashboard_players.json                # Player data (622 players)
├── dashboard_analytics.json              # Analytics insights
├── hadoop_spark_ipl_processor.py         # Data processing script
├── ipl_2025_auction_players.csv          # Source auction data
├── config/                               # Configuration files
├── data/                                 # Data directories
└── src/                                  # React/TypeScript source
```

## 🔧 Installation

### Prerequisites
- Node.js 16+ 
- Python 3.8+
- Hadoop 3.3.6+
- Apache Spark 3.5.0+

### Setup

```bash
# Install dependencies
npm install

# Process data with Hadoop/Spark
python3 hadoop_spark_ipl_processor.py

# Start development server
npm run dev

# Build production version
npm run build
```

## 🎯 Usage

### Run Dashboard Directly
```bash
firefox final_hadoop_spark_dashboard.html
```

### Process Data Pipeline
```bash
python3 hadoop_spark_ipl_processor.py
```

This will:
1. Load data from `ipl_2025_auction_players.csv`
2. Process with Hadoop/Spark analytics
3. Generate player statistics and insights
4. Store results in HDFS at `/ipl_auction_2025/`

## 📊 Data Sources

- **Primary**: `ipl_2025_auction_players.csv` - Official IPL 2025 auction data
- **Processed**: `dashboard_players.json` - Enhanced player data with analytics
- **Analytics**: `hadoop_analytics.json` - Team and budget analysis

## 🛠 Technology Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- Recharts (analytics visualization)
- Vite (build tool)

**Backend:**
- Hadoop 3.3.6 (data storage)
- Apache Spark 3.5.0 (data processing)
- Python 3.x (processing scripts)

## 📈 Features Breakdown

### Player Database
- 622 real auction players
- Accurate team affiliations (RCB, MI, CSK, KKR, SRH, GT, LSG, RR, DC, PBKS)
- Role classification (Batsman, Bowler, All-rounder, Wicket-keeper)
- Performance metrics (runs, wickets, strike rate, economy)

### Budget Management
- 120 Crore total budget
- Real-time tracking
- Color-coded price ranges
- Budget utilization visualization

### Advanced Filtering
- Search by player name
- Filter by team
- Filter by role
- Filter by budget range
- Real-time results with 300ms debounce

### Analytics Dashboard
- Team balance score (0-100)
- Batting/Bowling strength metrics
- Budget efficiency tracking
- Experience level analysis
- Team diversity measurement

## 🌐 Deployment

### Development
```bash
npm run dev
# Opens at http://localhost:5173
```

### Production
```bash
npm run build
# Output in dist/ directory
```

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ using Hadoop, Spark, and React**