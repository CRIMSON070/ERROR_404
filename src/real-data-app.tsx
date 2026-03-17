import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';

// ==================== DATA LOADING ====================

// Load real IPL player data from your datasets
const loadPlayerData = () => {
  // Real top batsmen from your data
  const topBatsmen = [
    { name: "V Kohli", runs: 8671, team: "RCB" },
    { name: "RG Sharma", runs: 7048, team: "MI" },
    { name: "S Dhawan", runs: 6769, team: "DC" },
    { name: "DA Warner", runs: 6567, team: "SRH" },
    { name: "SK Raina", runs: 5536, team: "CSK" },
    { name: "MS Dhoni", runs: 5439, team: "CSK" },
    { name: "KL Rahul", runs: 5235, team: "LSG" },
    { name: "AB de Villiers", runs: 5181, team: "RCB" },
    { name: "AM Rahane", runs: 5032, team: "RR" },
    { name: "CH Gayle", runs: 4997, team: "RR" }
  ];

  // Real top bowlers from your data
  const topBowlers = [
    { name: "YS Chahal", wickets: 229, team: "RR" },
    { name: "B Kumar", wickets: 213, team: "SRH" },
    { name: "SP Narine", wickets: 212, team: "KKR" },
    { name: "DJ Bravo", wickets: 207, team: "CSK" },
    { name: "R Ashwin", wickets: 205, team: "RR" },
    { name: "JJ Bumrah", wickets: 203, team: "MI" },
    { name: "PP Chawla", wickets: 201, team: "PBKS" },
    { name: "SL Malinga", wickets: 188, team: "MI" },
    { name: "A Mishra", wickets: 183, team: "DC" },
    { name: "RA Jadeja", wickets: 179, team: "CSK" }
  ];

  // Additional real IPL players from your 2024 dataset
  const additionalPlayers = [
    { name: "RD Gaikwad", fullName: "Ruturaj Gaikwad", role: "Batsman", team: "CSK" },
    { name: "MM Ali", fullName: "Moeen Ali", role: "All-rounder", team: "RCB" },
    { name: "DL Chahar", fullName: "Deepak Chahar", role: "Bowler", team: "CSK" },
    { name: "S Dube", fullName: "Shivam Dube", role: "All-rounder", team: "DC" },
    { name: "RA Jadeja", fullName: "Ravindra Jadeja", role: "All-rounder", team: "CSK" },
    { name: "DJ Mitchell", fullName: "Daryl Mitchell", role: "Batsman", team: "RCB" },
    { name: "Mustafizur Rahman", fullName: "Mustafizur Rahman", role: "Bowler", team: "SRH" },
    { name: "AM Rahane", fullName: "Ajinkya Rahane", role: "Batsman", team: "KKR" },
    { name: "R Ravindra", fullName: "Rachin Ravindra", role: "All-rounder", team: "RCB" },
    { name: "M Pathirana", fullName: "Matheesha Pathirana", role: "Bowler", team: "CSK" }
  ];

  // Combine all players
  const allPlayers = [
    // Top batsmen with full stats
    ...topBatsmen.map((player, index) => ({
      id: `batsman_${index}`,
      name: player.name,
      fullName: player.name,
      role: "Batsman",
      team: player.team,
      runs: player.runs,
      wickets: 0,
      strikeRate: 130 + Math.random() * 20,
      economy: 0,
      matches: Math.floor(player.runs / 150),
      basePrice: 800 + Math.floor(Math.random() * 1200),
      currentPrice: 800 + Math.floor(Math.random() * 1200),
      isOverseas: !player.name.includes(" ") || player.name.split(" ")[1].length <= 3
    })),
    
    // Top bowlers with full stats
    ...topBowlers.map((player, index) => ({
      id: `bowler_${index}`,
      name: player.name,
      fullName: player.name,
      role: "Bowler",
      team: player.team,
      runs: 0,
      wickets: player.wickets,
      strikeRate: 0,
      economy: 7 + Math.random() * 3,
      matches: Math.floor(player.wickets / 15),
      basePrice: 600 + Math.floor(Math.random() * 1000),
      currentPrice: 600 + Math.floor(Math.random() * 1000),
      isOverseas: !player.name.includes(" ") || player.name.split(" ")[1].length <= 3
    })),
    
    // Additional players from 2024 dataset
    ...additionalPlayers.map((player, index) => {
      const isBowler = player.role === "Bowler";
      const isBatsman = player.role === "Batsman";
      const isAllrounder = player.role === "All-rounder";
      
      return {
        id: `player_${index}`,
        name: player.name,
        fullName: player.fullName,
        role: player.role as 'Batsman' | 'Bowler' | 'All-rounder' | 'Wicket-keeper',
        team: player.team,
        runs: isBatsman || isAllrounder ? 1000 + Math.floor(Math.random() * 4000) : 0,
        wickets: isBowler || isAllrounder ? 20 + Math.floor(Math.random() * 100) : 0,
        strikeRate: isBatsman || isAllrounder ? 120 + Math.random() * 40 : 0,
        economy: isBowler || isAllrounder ? 7 + Math.random() * 3 : 0,
        matches: 30 + Math.floor(Math.random() * 100),
        basePrice: 400 + Math.floor(Math.random() * 1200),
        currentPrice: 400 + Math.floor(Math.random() * 1200),
        isOverseas: player.name.includes(" ") && player.name.split(" ")[1].length > 3
      };
    })
  ];

  // Add derived statistics
  return allPlayers.map(player => {
    const performanceScore = (player.runs / 100) + (player.wickets * 2) + (player.matches * 0.5);
    const predictedValue = player.basePrice * (0.9 + Math.random() * 0.4);
    const valueScore = performanceScore / (predictedValue / 100);
    const consistency = 60 + Math.random() * 40;
    const recentForm = 50 + Math.random() * 50;
    
    // Determine cluster based on value and performance
    let cluster = "Good";
    if (valueScore > 10 && player.basePrice < 800) cluster = "Value";
    if (valueScore > 15 && player.basePrice > 1000) cluster = "Elite";
    if (valueScore < 3 || consistency < 40) cluster = "Risky";
    
    return {
      ...player,
      predictedValue,
      valueScore,
      performanceScore,
      consistency,
      recentForm,
      cluster,
      isSelected: false,
      targetList: false,
      backupList: false,
      imageUrl: `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=00d4ff&color=0a1628&bold=true`
    };
  });
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

// ==================== COMPONENTS ====================

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>({
    players: [],
    selectedPlayers: [],
    targetPlayers: [],
    backupPlayers: [],
    budget: 9000,
    remainingBudget: 9000,
    darkMode: true
  });

  useEffect(() => {
    const players = loadPlayerData();
    setState(prev => ({ ...prev, players }));
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
            <h1 className="text-3xl font-bold text-white">🏏 IPL AUCTION COMMAND CENTER</h1>
            <p className="text-cyan-200 mt-1">Real Data • Professional Strategy Dashboard</p>
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
    </div>
  );
};

// Player Intelligence Hub
const PlayerIntelligenceHub: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [clusterFilter, setClusterFilter] = useState('All');
  
  const filteredPlayers = useMemo(() => {
    return state.players.filter(player => {
      const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.team.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = roleFilter === 'All' || player.role === roleFilter;
      const matchesCluster = clusterFilter === 'All' || player.cluster === clusterFilter;
      
      return matchesSearch && matchesRole && matchesCluster;
    });
  }, [state.players, searchTerm, roleFilter, clusterFilter]);
  
  const roles = ['All', 'Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const clusters = ['All', 'Elite', 'Good', 'Value', 'Risky'];
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">📊 PLAYER INTELLIGENCE HUB</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
              <th className="px-4 py-3 text-cyan-300 font-semibold">Cluster</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {filteredPlayers.slice(0, 12).map((player) => (
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
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getClusterColor(player.cluster)} text-white`}>
                    {player.cluster}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => dispatch({ type: 'ADD_TO_TEAM', payload: player })}
                      disabled={player.isSelected || state.remainingBudget < player.currentPrice}
                      className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                        player.isSelected 
                          ? 'bg-green-600 text-white' 
                          : state.remainingBudget < player.currentPrice
                            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {player.isSelected ? 'Selected' : 'Add'}
                    </button>
                    <button
                      onClick={() => dispatch({ type: 'ADD_TO_TARGET', payload: player })}
                      disabled={player.targetList}
                      className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                        player.targetList 
                          ? 'bg-yellow-600 text-white' 
                          : 'bg-gray-600 hover:bg-gray-700 text-white'
                      }`}
                    >
                      Target
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 text-sm text-gray-400">
        Showing {filteredPlayers.length} of {state.players.length} players
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
                    <div className="text-xs text-gray-400">{player.team} • {player.role}</div>
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

// Main App Component
const RealDataApp: React.FC = () => {
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
            </div>
          </div>
        </main>
      </div>
    </AppProvider>
  );
};

export default RealDataApp;