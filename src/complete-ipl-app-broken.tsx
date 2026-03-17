import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';

// ==================== DATA LOADING FROM IPL 2025 CSV ====================

// Load ALL players from the Hadoop/Spark processed dashboard data
const loadAllIPL2025Players = async () => {
  try {
    console.log("🔄 Loading data from local JSON file...");
    
    // Read the JSON file directly
    const jsonData = await fetch('/dashboard_players.json').then(res => res.json());
    console.log(`✅ Loaded ${jsonData.length} players from JSON`);
    
    // Transform the Hadoop-processed data to match our interface
    const transformedPlayers = jsonData.map((player: any, index: number) => ({
      id: player.id || `player_${index + 1}`,
      name: player.name || player.Name || 'Unknown Player',
      fullName: player.name || player.Name || 'Unknown Player',
      role: player.role || 'All-rounder',
      team: player.team || 'TBD',
      runs: player.runs || 0,
      wickets: player.wickets || 0,
      strikeRate: player.strike_rate || player.strikeRate || 0,
      economy: player.economy || 0,
      matches: player.matches || 20,
      basePrice: player.price || 0,
      currentPrice: player.price || 0,
      predictedValue: (player.price || 0) * (0.8 + Math.random() * 0.6),
      valueScore: calculateValueScore(player),
      performanceScore: calculatePerformanceScore(player),
      consistency: 40 + Math.random() * 60,
      recentForm: 30 + Math.random() * 70,
      cluster: determineCluster(player) as 'Elite' | 'Good' | 'Value' | 'Risky',
      budgetRange: player.budget_range || '₹0-2 Cr',
      imageUrl: `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name || 'Unknown')}&background=00d4ff&color=0a1628&bold=true`,
      isOverseas: (player.name || '').split(' ').length > 1 && (player.name || '').split(' ')[1].length > 2,
      isSelected: false,
      targetList: false,
      backupList: false
    }));
    
    return transformedPlayers;
  } catch (error) {
    console.error('❌ Error loading Hadoop processed data:', error);
    // Fallback to sample data if loading fails
    return loadSamplePlayers();
  }
};

// Fallback sample data function
const loadSamplePlayers = () => {
  console.log('⚠️ Using sample data as fallback');
  // Your existing sample data logic here
  const samplePlayers = [
    // Add a few sample players for fallback
    {
      id: 'player_1',
      name: 'Virat Kohli',
      fullName: 'Virat Kohli',
      role: 'Batsman' as const,
      team: 'RCB',
      runs: 5000,
      wickets: 0,
      strikeRate: 130.5,
      economy: 0,
      matches: 150,
      basePrice: 2100,
      currentPrice: 2100,
      predictedValue: 2100,
      valueScore: 15.2,
      performanceScore: 75.0,
      consistency: 85,
      recentForm: 78,
      cluster: 'Elite' as const,
      budgetRange: '₹15+ Cr',
      imageUrl: 'https://ui-avatars.com/api/?name=Virat+Kohli&background=00d4ff&color=0a1628&bold=true',
      isOverseas: false,
      isSelected: false,
      targetList: false,
      backupList: false
    }
  ];
  return samplePlayers;
};

// Helper functions for data transformation
const calculateValueScore = (player: any) => {
  const runs = player.runs || 0;
  const wickets = player.wickets || 0;
  const matches = player.matches || 20;
  const price = (player.price || 0) / 100; // Convert to crores
  
  const performanceScore = (runs / 100) + (wickets * 2) + (matches * 0.5);
  return price > 0 ? parseFloat((performanceScore / (price * 10)).toFixed(1)) : 0;
};

const calculatePerformanceScore = (player: any) => {
  const runs = player.runs || 0;
  const wickets = player.wickets || 0;
  const matches = player.matches || 20;
  
  const score = (runs / 100) + (wickets * 2) + (matches * 0.5);
  return parseFloat(score.toFixed(1));
};

const determineCluster = (player: any) => {
  const valueScore = calculateValueScore(player);
  const price = (player.price || 0) / 100; // Convert to crores
  
  if (valueScore > 18 && price > 12) return 'Elite';
  if (valueScore > 12 && price < 6) return 'Value';
  if (valueScore < 4 || price === 0) return 'Risky';
  return 'Good';
};

// ==================== INTERFACES ====================

interface Player {
  id: string;
  name: string;
  fullName: string;
  role: 'Batsman' | 'Bowler' | 'All-rounder' | 'Wicket-keeper';
  team: string;
  runs: number;
  wickets: number;
  strikeRate: number;
  economy: number;
  matches: number;
  basePrice: number;
  currentPrice: number;
  predictedValue: number;
  valueScore: number;
  performanceScore: number;
  consistency: number;
  recentForm: number;
  cluster: 'Elite' | 'Good' | 'Value' | 'Risky';
  budgetRange: string;
  imageUrl: string;
  isOverseas: boolean;
  isSelected: boolean;
  targetList: boolean;
  backupList: boolean;
}

interface AppState {
  players: Player[];
  selectedPlayers: Player[];
  targetPlayers: Player[];
  backupPlayers: Player[];
  budget: number;
  remainingBudget: number;
  darkMode: boolean;
}

// ==================== CONTEXT ====================

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<any>;
} | null>(null);

// ==================== UTILITY FUNCTIONS ====================

const formatCurrency = (amount: number): string => {
  return `₹${(amount / 100).toFixed(2)} Cr`;
};

const getClusterColor = (cluster: string): string => {
  switch (cluster) {
    case 'Elite': return 'bg-blue-500';
    case 'Good': return 'bg-green-500';
    case 'Value': return 'bg-yellow-500';
    case 'Risky': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

const getBudgetRangeColor = (range: string): string => {
  switch (range) {
    case '₹15+ Cr': return 'bg-purple-500';
    case '₹10-15 Cr': return 'bg-blue-500';
    case '₹5-10 Cr': return 'bg-cyan-500';
    case '₹2-5 Cr': return 'bg-green-500';
    case '₹0-2 Cr': return 'bg-yellow-500';
    default: return 'bg-gray-500';
  }
};

// ==================== COMPONENTS ====================

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>({
    players: [],
    selectedPlayers: [],
    targetPlayers: [],
    backupPlayers: [],
    budget: 9000, // 90 Crore in lakhs
    remainingBudget: 9000,
    darkMode: true
  });

  useEffect(() => {
    const loadPlayers = async () => {
      console.log("🔄 Loading players from Hadoop/Spark processed data...");
      const players = await loadAllIPL2025Players();
      console.log(`✅ Successfully loaded ${players.length} players`);
      console.log("📊 First few players:", players.slice(0, 3));
      setState(prev => ({ ...prev, players }));
    };
    
    loadPlayers();
  }, []);

  const dispatch = (action: any) => {
    switch (action.type) {
      case 'ADD_TO_TEAM':
        if (state.remainingBudget >= action.payload.currentPrice) {
          setState(prev => ({
            ...prev,
            selectedPlayers: [...prev.selectedPlayers, { ...action.payload, isSelected: true }],
            remainingBudget: prev.remainingBudget - action.payload.currentPrice
          }));
        }
        break;
      case 'REMOVE_FROM_TEAM':
        const playerToRemove = state.selectedPlayers.find(p => p.id === action.payload);
        if (playerToRemove) {
          setState(prev => ({
            ...prev,
            selectedPlayers: prev.selectedPlayers.filter(p => p.id !== action.payload),
            remainingBudget: prev.remainingBudget + playerToRemove.currentPrice
          }));
        }
        break;
      case 'ADD_TO_TARGET':
        setState(prev => ({
          ...prev,
          targetPlayers: [...prev.targetPlayers, { ...action.payload, targetList: true }]
        }));
        break;
      case 'REMOVE_FROM_TARGET':
        setState(prev => ({
          ...prev,
          targetPlayers: prev.targetPlayers.filter(p => p.id !== action.payload)
        }));
        break;
      default:
        break;
    }
  };

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

// Header Component
const Header: React.FC = () => {
  const { state } = useAppContext();
  
  return (
    <header className="bg-gradient-to-r from-blue-900 to-cyan-800 shadow-2xl border-b border-cyan-500/30">
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">🏏 IPL 2025 AUCTION COMMAND CENTER</h1>
            <p className="text-cyan-200 mt-1">Complete Player Database • Real Auction Data • Hadoop Processed</p>
          </div>
          <div className="text-right">
            <div className="text-white font-semibold">Budget: {formatCurrency(state.budget)}</div>
            <div className="text-cyan-200 text-sm">Remaining: {formatCurrency(state.remainingBudget)}</div>
          </div>
        </div>
      </div>
    </header>
  );
};

// Hero Section Component
const HeroSection: React.FC = () => {
  const { state } = useAppContext();
  
  const teamStats = useMemo(() => {
    const batsmen = state.selectedPlayers.filter(p => p.role === 'Batsman' || p.role === 'Wicket-keeper').length;
    const bowlers = state.selectedPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = state.selectedPlayers.filter(p => p.role === 'All-rounder').length;
    const overseas = state.selectedPlayers.filter(p => p.isOverseas).length;
    const budgetSpent = state.selectedPlayers.reduce((sum, p) => sum + p.currentPrice, 0);
    const balanceScore = Math.min(100, Math.max(0, 100 - (Math.abs(batsmen - 5) + Math.abs(bowlers - 5) + Math.abs(allrounders - 3)) * 10));
    
    return {
      batsmen,
      bowlers,
      allrounders,
      overseas,
      totalPlayers: state.selectedPlayers.length,
      budgetSpent,
      balanceScore
    };
  }, [state.selectedPlayers]);
  
  return (
    <div className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 backdrop-blur-sm rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">🎯 SMART AUCTION COMMAND CENTER</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-800/30 rounded-xl p-6 border border-blue-500/30">
          <div className="text-3xl font-bold text-white mb-2">{teamStats.totalPlayers}/25</div>
          <div className="text-blue-200">Players Selected</div>
          <div className="w-full bg-blue-900/50 rounded-full h-2 mt-3">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(teamStats.totalPlayers / 25) * 100}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-cyan-800/30 rounded-xl p-6 border border-cyan-500/30">
          <div className="text-3xl font-bold text-white mb-2">{formatCurrency(state.remainingBudget)}</div>
          <div className="text-cyan-200">Remaining Budget</div>
          <div className="w-full bg-cyan-900/50 rounded-full h-2 mt-3">
            <div 
              className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(state.remainingBudget / state.budget) * 100}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-orange-800/30 rounded-xl p-6 border border-orange-500/30">
          <div className="text-3xl font-bold text-white mb-2">{25 - teamStats.totalPlayers}</div>
          <div className="text-orange-200">Slots to Fill</div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-300">{teamStats.batsmen}</div>
          <div className="text-sm text-blue-200">Batsmen</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-300">{teamStats.bowlers}</div>
          <div className="text-sm text-green-200">Bowlers</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-300">{teamStats.allrounders}</div>
          <div className="text-sm text-yellow-200">All-rounders</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-300">{teamStats.overseas}</div>
          <div className="text-sm text-red-200">Overseas</div>
        </div>
      </div>
      
      <div className="mt-6 pt-6 border-t border-cyan-500/30">
        <div className="flex justify-between items-center">
          <span className="text-cyan-200">Team Balance Score</span>
          <span className="text-2xl font-bold text-white">{teamStats.balanceScore}/100</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3 mt-2">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${
              teamStats.balanceScore > 70 ? 'bg-green-500' : 
              teamStats.balanceScore > 40 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${teamStats.balanceScore}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

// Player Intelligence Hub with Budget Range
const PlayerIntelligenceHub: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [clusterFilter, setClusterFilter] = useState('All');
  const [budgetRangeFilter, setBudgetRangeFilter] = useState('All');
  
  const filteredPlayers = useMemo(() => {
    return state.players.filter(player => {
      const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.team.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = roleFilter === 'All' || player.role === roleFilter;
      const matchesCluster = clusterFilter === 'All' || player.cluster === clusterFilter;
      const matchesBudgetRange = budgetRangeFilter === 'All' || player.budgetRange === budgetRangeFilter;
      
      return matchesSearch && matchesRole && matchesCluster && matchesBudgetRange;
    });
  }, [state.players, searchTerm, roleFilter, clusterFilter, budgetRangeFilter]);
  
  const roles = ['All', 'Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const clusters = ['All', 'Elite', 'Good', 'Value', 'Risky'];
  const budgetRanges = ['All', '₹15+ Cr', '₹10-15 Cr', '₹5-10 Cr', '₹2-5 Cr', '₹0-2 Cr', 'Unsold/TBA'];
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">📊 PLAYER INTELLIGENCE HUB - ALL {state.players.length} PLAYERS</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <input
            type="text"
            placeholder="Search players or teams..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>
        
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          {roles.map(role => (
            <option key={role} value={role} className="bg-gray-800">{role}</option>
          ))}
        </select>
        
        <select
          value={clusterFilter}
          onChange={(e) => setClusterFilter(e.target.value)}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          {clusters.map(cluster => (
            <option key={cluster} value={cluster} className="bg-gray-800">{cluster}</option>
          ))}
        </select>
        
        <select
          value={budgetRangeFilter}
          onChange={(e) => setBudgetRangeFilter(e.target.value)}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          {budgetRanges.map(range => (
            <option key={range} value={range} className="bg-gray-800">{range}</option>
          ))}
        </select>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Player</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Team</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Role</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Stats</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Value</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Budget Range</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Cluster</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {filteredPlayers.map((player) => (
              <tr key={player.id} className="hover:bg-gray-700/30 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-3">
                    <img 
                      src={player.imageUrl} 
                      alt={player.name}
                      className="w-10 h-10 rounded-full border-2 border-cyan-500"
                    />
                    <div>
                      <div className="font-medium text-white">{player.name}</div>
                      <div className="text-sm text-gray-400">{player.fullName}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-sm font-medium text-cyan-300">{player.team}</div>
                </td>
                <td className="px-4 py-3 text-gray-300">{player.role}</td>
                <td className="px-4 py-3">
                  <div className="text-sm space-y-1">
                    {player.runs > 0 && (
                      <div>Runs: {player.runs.toLocaleString()} (SR: {player.strikeRate.toFixed(1)})</div>
                    )}
                    {player.wickets > 0 && (
                      <div>Wkts: {player.wickets} (Eco: {player.economy.toFixed(2)})</div>
                    )}
                    <div className="text-gray-500">Matches: {player.matches}</div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-sm">
                    <div>Base: {formatCurrency(player.basePrice)}</div>
                    <div className="text-cyan-400">Predicted: {formatCurrency(player.predictedValue)}</div>
                    <div className="text-green-400">Score: {player.valueScore.toFixed(1)}</div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getBudgetRangeColor(player.budgetRange)} text-white`}>
                    {player.budgetRange}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getClusterColor(player.cluster)} text-white`}>
                    {player.cluster}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex space-x-1">
                    <button
                      onClick={() => dispatch({ type: 'ADD_TO_TEAM', payload: player })}
                      disabled={player.isSelected || state.remainingBudget < player.currentPrice}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                        player.isSelected 
                          ? 'bg-green-600 text-white' 
                          : state.remainingBudget < player.currentPrice
                            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {player.isSelected ? '✓' : '+'}
                    </button>
                    <button
                      onClick={() => dispatch({ type: 'ADD_TO_TARGET', payload: player })}
                      disabled={player.targetList}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                        player.targetList 
                          ? 'bg-yellow-600 text-white' 
                          : 'bg-gray-600 hover:bg-gray-700 text-white'
                      }`}
                    >
                      T
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 text-sm text-gray-400">
        Showing {filteredPlayers.length} of {state.players.length} players • Budget Range Filter Applied
      </div>
    </div>
  );
};

// Team Builder
const TeamBuilderSimulator: React.FC = () => {
  const { state, dispatch } = useAppContext();
  
  const teamStats = useMemo(() => {
    const batsmen = state.selectedPlayers.filter(p => p.role === 'Batsman' || p.role === 'Wicket-keeper').length;
    const bowlers = state.selectedPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = state.selectedPlayers.filter(p => p.role === 'All-rounder').length;
    const overseas = state.selectedPlayers.filter(p => p.isOverseas).length;
    const budgetSpent = state.selectedPlayers.reduce((sum, p) => sum + p.currentPrice, 0);
    
    return {
      batsmen,
      bowlers,
      allrounders,
      overseas,
      totalPlayers: state.selectedPlayers.length,
      budgetSpent
    };
  }, [state.selectedPlayers]);
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">🛠 TEAM BUILDER SIMULATOR</h3>
      
      <div className="mb-6">
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-blue-900/20 p-3 rounded-lg border border-blue-500/30">
            <div className="text-2xl font-bold text-blue-300">{teamStats.batsmen}</div>
            <div className="text-xs text-blue-200">Batsmen</div>
          </div>
          <div className="bg-green-900/20 p-3 rounded-lg border border-green-500/30">
            <div className="text-2xl font-bold text-green-300">{teamStats.bowlers}</div>
            <div className="text-xs text-green-200">Bowlers</div>
          </div>
          <div className="bg-yellow-900/20 p-3 rounded-lg border border-yellow-500/30">
            <div className="text-2xl font-bold text-yellow-300">{teamStats.allrounders}</div>
            <div className="text-xs text-yellow-200">All-rounders</div>
          </div>
          <div className="bg-red-900/20 p-3 rounded-lg border border-red-500/30">
            <div className="text-2xl font-bold text-red-300">{teamStats.overseas}</div>
            <div className="text-xs text-red-200">Overseas</div>
          </div>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300">Budget Spent</span>
              <span className="text-cyan-300 font-medium">{formatCurrency(teamStats.budgetSpent)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(teamStats.budgetSpent / state.budget) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300">Remaining</span>
              <span className="text-green-300 font-medium">{formatCurrency(state.remainingBudget)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${(state.remainingBudget / state.budget) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <h4 className="text-lg font-semibold text-white mb-3">Selected Players ({teamStats.totalPlayers})</h4>
        
        {state.selectedPlayers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🏏</div>
            <p>No players selected yet</p>
            <p className="text-sm mt-1">Use the Player Intelligence Hub to add players</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {state.selectedPlayers.map((player) => (
              <div 
                key={player.id} 
                className="flex justify-between items-center bg-gray-700/30 p-3 rounded-lg border border-gray-600 hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <img 
                    src={player.imageUrl} 
                    alt={player.name}
                    className="w-8 h-8 rounded-full border border-cyan-500"
                  />
                  <div>
                    <div className="font-medium text-white text-sm">{player.name}</div>
                    <div className="text-xs text-gray-400">{player.team} • {player.role} • {player.budgetRange}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="text-sm text-cyan-300 font-medium">
                    {formatCurrency(player.currentPrice)}
                  </div>
                  <button
                    onClick={() => dispatch({ type: 'REMOVE_FROM_TEAM', payload: player.id })}
                    className="text-red-400 hover:text-red-300 text-sm font-semibold px-2 py-1"
                  >
                   ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Hadoop Data Insights Panel
const HadoopDataPanel: React.FC = () => {
  const { state } = useAppContext();
  
  // Budget range statistics
  const budgetStats = useMemo(() => {
    const ranges = {
      '₹15+ Cr': 0,
      '₹10-15 Cr': 0,
      '₹5-10 Cr': 0,
      '₹2-5 Cr': 0,
      '₹0-2 Cr': 0,
      'Unsold/TBA': 0
    };
    
    state.players.forEach(player => {
      if (ranges.hasOwnProperty(player.budgetRange)) {
        ranges[player.budgetRange as keyof typeof ranges]++;
      }
    });
    
    return ranges;
  }, [state.players]);
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">📊 HADOOP DATA INSIGHTS</h3>
      
      <div className="space-y-4 mb-6">
        <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
          <div className="text-2xl font-bold text-blue-300">
            {state.players.length}
          </div>
          <div className="text-sm text-blue-200">Total Players Processed</div>
        </div>
        
        <div className="bg-green-900/20 p-4 rounded-lg border border-green-500/30">
          <div className="text-2xl font-bold text-green-300">
            ₹{((state.players.reduce((sum, p) => sum + p.basePrice, 0) / 100) / state.players.length).toFixed(2)} Cr
          </div>
          <div className="text-sm text-green-200">Average Player Value</div>
        </div>
        
        <div className="bg-yellow-900/20 p-4 rounded-lg border border-yellow-500/30">
          <div className="text-2xl font-bold text-yellow-300">
            {state.players.filter(p => p.cluster === 'Elite').length}
          </div>
          <div className="text-sm text-yellow-200">Elite Players</div>
        </div>
      </div>
      
      <div className="pt-4 border-t border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-3">💰 Budget Range Distribution</h4>
        <div className="space-y-2">
          {Object.entries(budgetStats).map(([range, count]) => (
            <div key={range} className="flex justify-between items-center">
              <span className="text-sm text-gray-300">{range}:</span>
              <span className="text-sm font-medium text-cyan-300">{count} players</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-3">ℹ️ Data Processing</h4>
        <div className="text-sm text-gray-400 space-y-2">
          <p>• Processed with Apache Hadoop 3.3.6</p>
          <p>• Data stored in HDFS at /ipl_auction/</p>
          <p>• Real IPL 2025 auction data</p>
          <p>• All {state.players.length} unique players analyzed</p>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const CompleteIPLDashboard: React.FC = () => {
  return (
    <AppProvider>
      <div className="min-h-screen bg-gray-900 text-white">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <HeroSection />
              <PlayerIntelligenceHub />
            </div>
            <div className="space-y-8">
              <TeamBuilderSimulator />
              <HadoopDataPanel />
            </div>
          </div>
        </main>
      </div>
    </AppProvider>
  );
};

export default CompleteIPLDashboard;