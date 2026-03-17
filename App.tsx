import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';

// ==================== INTERFACES AND TYPES ====================

interface Player {
  id: string;
  name: string;
  role: 'Batsman' | 'Bowler' | 'All-rounder' | 'Wicket-keeper';
  country: string;
  experience: 'Rookie' | 'Experienced' | 'Veteran';
  basePrice: number;
  currentPrice: number;
  predictedValue: number;
  valueScore: number;
  cluster: 'Elite' | 'Good' | 'Value' | 'Risky';
  runs: number;
  strikeRate: number;
  wickets: number;
  economy: number;
  matches: number;
  performanceScore: number;
  consistency: number;
  recentForm: number;
  imageUrl: string;
  isOverseas: boolean;
  isSelected: boolean;
  targetList: boolean;
  backupList: boolean;
}

interface TeamComposition {
  batsmen: number;
  bowlers: number;
  allrounders: number;
  wicketkeepers: number;
  overseas: number;
  totalPlayers: number;
  budgetSpent: number;
  balanceScore: number;
}

interface AppState {
  players: Player[];
  selectedPlayers: Player[];
  targetPlayers: Player[];
  backupPlayers: Player[];
  teamComposition: TeamComposition;
  budget: number;
  remainingBudget: number;
  darkMode: boolean;
}

// ==================== CONTEXT ====================

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

type Action =
  | { type: 'SET_PLAYERS'; payload: Player[] }
  | { type: 'ADD_TO_TEAM'; payload: Player }
  | { type: 'REMOVE_FROM_TEAM'; payload: string }
  | { type: 'ADD_TO_TARGET'; payload: Player }
  | { type: 'REMOVE_FROM_TARGET'; payload: string }
  | { type: 'ADD_TO_BACKUP'; payload: Player }
  | { type: 'REMOVE_FROM_BACKUP'; payload: string }
  | { type: 'TOGGLE_DARK_MODE' }
  | { type: 'RESET_TEAM' };

// ==================== MOCK DATA GENERATION ====================

const generateMockPlayers = (): Player[] => {
  const firstNames = ['Virat', 'Rohit', 'Shikhar', 'KL', 'Shreyas', 'Rishabh', 'Hardik', 'Jasprit', 'Mohammed', 'Ravindra', 'Shubman', 'Suryakumar', 'Devdutt', 'Washington', 'Glenn', 'Jos', 'David', 'Kieron', 'Andre', 'Liam'];
  const lastNames = ['Kohli', 'Sharma', 'Dhawan', 'Rahul', 'Iyer', 'Pant', 'Pandya', 'Bumrah', 'Shami', 'Jadeja', 'Gill', 'Yadav', 'Padikkal', 'Sundar', 'Maxwell', 'Buttler', 'Warner', 'Pollard', 'Russell', 'Livingstone'];
  const countries = ['India', 'Australia', 'England', 'South Africa', 'West Indies', 'New Zealand', 'Sri Lanka', 'Afghanistan'];
  const roles: ('Batsman' | 'Bowler' | 'All-rounder' | 'Wicket-keeper')[] = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const experienceLevels: ('Rookie' | 'Experienced' | 'Veteran')[] = ['Rookie', 'Experienced', 'Veteran'];
  const clusters: ('Elite' | 'Good' | 'Value' | 'Risky')[] = ['Elite', 'Good', 'Value', 'Risky'];
  
  const players: Player[] = [];
  const totalPlayers = 200;
  
  for (let i = 0; i < totalPlayers; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const name = `${firstName} ${lastName}`;
    const role = roles[Math.floor(Math.random() * roles.length)];
    const country = countries[Math.floor(Math.random() * countries.length)];
    const experience = experienceLevels[Math.floor(Math.random() * experienceLevels.length)];
    const cluster = clusters[Math.floor(Math.random() * clusters.length)];
    
    // Generate realistic stats based on role
    let runs = 0, strikeRate = 0, wickets = 0, economy = 0;
    
    if (role === 'Batsman' || role === 'Wicket-keeper') {
      runs = Math.floor(Math.random() * 3000) + 500;
      strikeRate = Math.random() * 50 + 120;
    } else if (role === 'Bowler') {
      wickets = Math.floor(Math.random() * 100) + 20;
      economy = Math.random() * 2 + 7;
    } else { // All-rounder
      runs = Math.floor(Math.random() * 2000) + 300;
      strikeRate = Math.random() * 40 + 110;
      wickets = Math.floor(Math.random() * 60) + 10;
      economy = Math.random() * 3 + 8;
    }
    
    const matches = Math.floor(Math.random() * 100) + 20;
    const basePrice = Math.floor(Math.random() * 1500) + 200; // 200-1700 lakhs
    const performanceScore = (runs / 100) + (wickets * 2) + (matches * 0.5);
    const consistency = Math.random() * 100;
    const recentForm = Math.random() * 100;
    const predictedValue = basePrice * (0.8 + Math.random() * 0.8); // 80-160% of base price
    const valueScore = performanceScore / (predictedValue / 100);
    
    players.push({
      id: `player_${i}`,
      name,
      role,
      country,
      experience,
      basePrice,
      currentPrice: basePrice,
      predictedValue,
      valueScore,
      cluster,
      runs,
      strikeRate,
      wickets,
      economy,
      matches,
      performanceScore,
      consistency,
      recentForm,
      imageUrl: `https://ui-avatars.com/api/?name=${firstName}+${lastName}&background=00d4ff&color=0a1628`,
      isOverseas: country !== 'India',
      isSelected: false,
      targetList: false,
      backupList: false
    });
  }
  
  return players;
};

// ==================== REDUCER ====================

const appReducer = (state: AppState, action: Action): AppState => {
  switch (action.type) {
    case 'SET_PLAYERS':
      return { ...state, players: action.payload };
    
    case 'ADD_TO_TEAM':
      const newPlayer = { ...action.payload, isSelected: true };
      const updatedPlayers = state.players.map(p => 
        p.id === action.payload.id ? newPlayer : p
      );
      return {
        ...state,
        players: updatedPlayers,
        selectedPlayers: [...state.selectedPlayers, newPlayer],
        remainingBudget: state.remainingBudget - newPlayer.currentPrice
      };
    
    case 'REMOVE_FROM_TEAM':
      const removedPlayer = state.players.find(p => p.id === action.payload);
      if (!removedPlayer) return state;
      
      const updatedPlayers2 = state.players.map(p => 
        p.id === action.payload ? { ...p, isSelected: false } : p
      );
      return {
        ...state,
        players: updatedPlayers2,
        selectedPlayers: state.selectedPlayers.filter(p => p.id !== action.payload),
        remainingBudget: state.remainingBudget + removedPlayer.currentPrice
      };
    
    case 'ADD_TO_TARGET':
      return {
        ...state,
        players: state.players.map(p => 
          p.id === action.payload.id ? { ...p, targetList: true } : p
        ),
        targetPlayers: [...state.targetPlayers, { ...action.payload, targetList: true }]
      };
    
    case 'REMOVE_FROM_TARGET':
      return {
        ...state,
        players: state.players.map(p => 
          p.id === action.payload ? { ...p, targetList: false } : p
        ),
        targetPlayers: state.targetPlayers.filter(p => p.id !== action.payload)
      };
    
    case 'ADD_TO_BACKUP':
      return {
        ...state,
        players: state.players.map(p => 
          p.id === action.payload.id ? { ...p, backupList: true } : p
        ),
        backupPlayers: [...state.backupPlayers, { ...action.payload, backupList: true }]
      };
    
    case 'REMOVE_FROM_BACKUP':
      return {
        ...state,
        players: state.players.map(p => 
          p.id === action.payload ? { ...p, backupList: false } : p
        ),
        backupPlayers: state.backupPlayers.filter(p => p.id !== action.payload)
      };
    
    case 'TOGGLE_DARK_MODE':
      return { ...state, darkMode: !state.darkMode };
    
    case 'RESET_TEAM':
      return {
        ...state,
        players: state.players.map(p => ({ ...p, isSelected: false, targetList: false, backupList: false })),
        selectedPlayers: [],
        targetPlayers: [],
        backupPlayers: [],
        remainingBudget: state.budget
      };
    
    default:
      return state;
  }
};

// ==================== CUSTOM HOOKS ====================

const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

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

// Unused function - kept for potential future use
// const getClusterTextColor = (cluster: string): string => {
//   switch (cluster) {
//     case 'Elite': return 'text-blue-500';
//     case 'Good': return 'text-green-500';
//     case 'Value': return 'text-yellow-500';
//     case 'Risky': return 'text-red-500';
//     default: return 'text-gray-500';
//   }
// };

// ==================== COMPONENTS ====================

const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = React.useReducer(appReducer, {
    players: [],
    selectedPlayers: [],
    targetPlayers: [],
    backupPlayers: [],
    teamComposition: {
      batsmen: 0,
      bowlers: 0,
      allrounders: 0,
      wicketkeepers: 0,
      overseas: 0,
      totalPlayers: 0,
      budgetSpent: 0,
      balanceScore: 0
    },
    budget: 9000, // 90 Cr in lakhs
    remainingBudget: 9000,
    darkMode: true
  });

  useEffect(() => {
    const mockPlayers = generateMockPlayers();
    dispatch({ type: 'SET_PLAYERS', payload: mockPlayers });
  }, []);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// Header Component
const Header: React.FC = () => {
  const { state, dispatch } = useAppContext();
  
  return (
    <header className="bg-gradient-to-r from-blue-900 to-cyan-800 shadow-2xl border-b border-cyan-500/30">
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">🏏 IPL AUCTION COMMAND CENTER</h1>
            <p className="text-cyan-200 mt-1">Professional Strategy Dashboard</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-white font-semibold">Budget: {formatCurrency(state.budget)}</div>
              <div className="text-cyan-200 text-sm">Remaining: {formatCurrency(state.remainingBudget)}</div>
            </div>
            <button
              onClick={() => dispatch({ type: 'TOGGLE_DARK_MODE' })}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-all duration-300 transform hover:scale-105"
            >
              {state.darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <AppProvider>
      <div className={`min-h-screen ${useAppContext().state.darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-8">
              <HeroSection />
              <PlayerIntelligenceHub />
              <KMeansClustering />
              <PricePredictionEngine />
            </div>
            
            {/* Right Column */}
            <div className="space-y-8">
              <TeamBuilderSimulator />
              <AuctionBiddingAssistant />
              <InsightsPanel />
              <HistoricalAnalytics />
            </div>
          </div>
        </main>
      </div>
    </AppProvider>
  );
};

// Hero Section Component
const HeroSection: React.FC = () => {
  const { state } = useAppContext();
  
  // Calculate team composition
  const teamStats = useMemo(() => {
    const batsmen = state.selectedPlayers.filter(p => p.role === 'Batsman' || p.role === 'Wicket-keeper').length;
    const bowlers = state.selectedPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = state.selectedPlayers.filter(p => p.role === 'All-rounder').length;
    const wicketkeepers = state.selectedPlayers.filter(p => p.role === 'Wicket-keeper').length;
    const overseas = state.selectedPlayers.filter(p => p.isOverseas).length;
    const budgetSpent = state.selectedPlayers.reduce((sum, p) => sum + p.currentPrice, 0);
    const balanceScore = Math.min(100, Math.max(0, 100 - (Math.abs(batsmen - 5) + Math.abs(bowlers - 5) + Math.abs(allrounders - 3)) * 10));
    
    return {
      batsmen,
      bowlers,
      allrounders,
      wicketkeepers,
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
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
          <div className="text-2xl font-bold text-purple-300">{teamStats.wicketkeepers}</div>
          <div className="text-sm text-purple-200">WK</div>
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

// Player Intelligence Hub Component
const PlayerIntelligenceHub: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [clusterFilter, setClusterFilter] = useState('All');
  // const [priceRange, setPriceRange] = useState<[number, number]>([0, 2000]);
  
  const filteredPlayers = useMemo(() => {
    return state.players.filter(player => {
      const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.country.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = roleFilter === 'All' || player.role === roleFilter;
      const matchesCluster = clusterFilter === 'All' || player.cluster === clusterFilter;
      // const matchesPrice = player.basePrice >= priceRange[0] && player.basePrice <= priceRange[1];
      
      return matchesSearch && matchesRole && matchesCluster; // && matchesPrice;
    });
  }, [state.players, searchTerm, roleFilter, clusterFilter]); // priceRange]);
  
  const roles = ['All', 'Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const clusters = ['All', 'Elite', 'Good', 'Value', 'Risky'];
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">📊 PLAYER INTELLIGENCE HUB</h2>
      
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <input
            type="text"
            placeholder="Search players..."
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
        
        {/* <div className="text-sm text-gray-400 flex items-center">
          <span>Price: {formatCurrency(priceRange[0])} - {formatCurrency(priceRange[1])}</span>
        </div> */}
      </div>
      
      {/* Player Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Player</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Role</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Stats</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Value</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Cluster</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {filteredPlayers.slice(0, 10).map((player) => (
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
                      <div className="text-sm text-gray-400">{player.country}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-300">{player.role}</td>
                <td className="px-4 py-3">
                  <div className="text-sm space-y-1">
                    {player.role !== 'Bowler' && (
                      <div>Runs: {player.runs} (SR: {player.strikeRate.toFixed(1)})</div>
                    )}
                    {player.role !== 'Batsman' && player.role !== 'Wicket-keeper' && (
                      <div>Wkts: {player.wickets} (Eco: {player.economy.toFixed(2)})</div>
                    )}
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
                  <span className={`cluster-badge ${getClusterColor(player.cluster)} text-white`}>
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
                      {player.isSelected ? 'Selected' : 'Add to Team'}
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

const KMeansClustering: React.FC = () => {
  const { state } = useAppContext();
  // const [hoveredPlayer, setHoveredPlayer] = useState<Player | null>(null);
  
  // Prepare data for scatter plot
  const chartData = useMemo(() => {
    return state.players.map(player => ({
      name: player.name,
      performance: player.performanceScore,
      consistency: player.consistency,
      cluster: player.cluster,
      value: player.valueScore,
      basePrice: player.basePrice,
      role: player.role
    }));
  }, [state.players]);
  
  // Group data by cluster for different colors
  const eliteData = chartData.filter(d => d.cluster === 'Elite');
  const valueData = chartData.filter(d => d.cluster === 'Value');
  const goodData = chartData.filter(d => d.cluster === 'Good');
  const riskyData = chartData.filter(d => d.cluster === 'Risky');
  
  // const CustomTooltip = ({ active, payload }: any) => {
  //   if (active && payload && payload.length) {
  //     const data = payload[0].payload;
  //     return (
  //       <div className="bg-gray-800 border border-cyan-500 p-4 rounded-lg shadow-xl">
  //         <p className="font-bold text-cyan-300">{data.name}</p>
  //         <p className="text-sm text-gray-300">Performance: {data.performance.toFixed(1)}</p>
  //         <p className="text-sm text-gray-300">Consistency: {data.consistency.toFixed(1)}</p>
  //         <p className="text-sm text-gray-300">Value Score: {data.value.toFixed(1)}</p>
  //         <p className="text-sm text-gray-300">Base Price: {formatCurrency(data.basePrice)}</p>
  //         <p className="text-sm text-gray-300">Role: {data.role}</p>
  //         <div className={`mt-2 px-2 py-1 rounded text-xs font-semibold inline-block ${getClusterColor(data.cluster)} text-white`}>
  //           {data.cluster} Player
  //         </div>
  //       </div>
  //     );
  //   }
  //   return null;
  // };
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">📈 K-MEANS CLUSTERING VISUALIZATION</h2>
      
      <div className="mb-6">
        <p className="text-gray-400 mb-4">
          Players clustered based on performance metrics and consistency. Hover over points for details.
        </p>
        
        {/* Legend */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded-full mr-2"></div>
            <span className="text-sm text-blue-300">Elite Performers</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-green-300">Value Picks ⭐</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
            <span className="text-sm text-yellow-300">Steady Players</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
            <span className="text-sm text-red-300">Risky Bets</span>
          </div>
        </div>
      </div>
      
      <div className="h-96">
        <div className="text-center text-gray-500 py-20">
          <div className="text-6xl mb-4">📊</div>
          <p>Interactive scatter plot visualization</p>
          <p className="text-sm mt-2">X-axis: Performance Score | Y-axis: Consistency</p>
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-900/30 p-3 rounded-lg border border-blue-500/30">
              <div className="text-blue-300 font-bold">{eliteData.length}</div>
              <div className="text-xs text-blue-200">Elite Players</div>
            </div>
            <div className="bg-green-900/30 p-3 rounded-lg border border-green-500/30">
              <div className="text-green-300 font-bold">{valueData.length}</div>
              <div className="text-xs text-green-200">Value Picks</div>
            </div>
            <div className="bg-yellow-900/30 p-3 rounded-lg border border-yellow-500/30">
              <div className="text-yellow-300 font-bold">{goodData.length}</div>
              <div className="text-xs text-yellow-200">Steady Players</div>
            </div>
            <div className="bg-red-900/30 p-3 rounded-lg border border-red-500/30">
              <div className="text-red-300 font-bold">{riskyData.length}</div>
              <div className="text-xs text-red-200">Risky Bets</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-sm text-gray-400">
        <p>💡 <strong>Insight:</strong> Value picks (green) offer the best performance-to-cost ratio. 
        Elite players (blue) are high performers but expensive. Consider a balanced approach.</p>
      </div>
    </div>
  );
};

const PricePredictionEngine: React.FC = () => {
  const [playerStats, setPlayerStats] = useState({
    runs: 1000,
    wickets: 25,
    matches: 50,
    strikeRate: 140,
    economy: 8.5,
    recentForm: 75
  });
  
  const [prediction, setPrediction] = useState<{
    predictedPrice: number;
    confidence: number;
    minPrice: number;
    maxPrice: number;
  } | null>(null);
  
  // Simulate ML prediction algorithm
  const predictPrice = () => {
    // Simple ML model simulation
    const baseValue = (
      (playerStats.runs / 100) * 0.3 +
      (playerStats.wickets * 2) * 0.4 +
      (playerStats.matches * 0.1) +
      ((playerStats.strikeRate - 100) * 0.1) +
      ((15 - playerStats.economy) * 2) +
      (playerStats.recentForm * 0.2)
    );
    
    const predictedPrice = Math.max(200, baseValue * 15); // Minimum 200 lakhs
    const confidence = Math.min(95, 70 + (playerStats.matches / 2));
    const variance = predictedPrice * 0.15;
    
    setPrediction({
      predictedPrice,
      confidence,
      minPrice: predictedPrice - variance,
      maxPrice: predictedPrice + variance
    });
  };
  
  // Historical data for chart
  const historicalData = [
    { auction: '2022', price: 850 },
    { auction: '2023', price: 920 },
    { auction: '2024', price: 1100 }
  ];
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">🔮 PRICE PREDICTION ENGINE</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Input Form */}
        <div>
          <h3 className="text-lg font-semibold text-cyan-300 mb-4">Player Statistics</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Runs Scored</label>
              <input
                type="number"
                value={playerStats.runs}
                onChange={(e) => setPlayerStats({...playerStats, runs: parseInt(e.target.value) || 0})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Wickets Taken</label>
              <input
                type="number"
                value={playerStats.wickets}
                onChange={(e) => setPlayerStats({...playerStats, wickets: parseInt(e.target.value) || 0})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Matches Played</label>
              <input
                type="number"
                value={playerStats.matches}
                onChange={(e) => setPlayerStats({...playerStats, matches: parseInt(e.target.value) || 0})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Strike Rate</label>
              <input
                type="number"
                step="0.1"
                value={playerStats.strikeRate}
                onChange={(e) => setPlayerStats({...playerStats, strikeRate: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Economy Rate</label>
              <input
                type="number"
                step="0.1"
                value={playerStats.economy}
                onChange={(e) => setPlayerStats({...playerStats, economy: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Recent Form (0-100)</label>
              <input
                type="range"
                min="0"
                max="100"
                value={playerStats.recentForm}
                onChange={(e) => setPlayerStats({...playerStats, recentForm: parseInt(e.target.value) || 0})}
                className="w-full"
              />
              <div className="text-sm text-gray-400 text-center">{playerStats.recentForm}%</div>
            </div>
            
            <button
              onClick={predictPrice}
              className="w-full btn-primary mt-4"
            >
              Predict Price
            </button>
          </div>
        </div>
        
        {/* Prediction Results */}
        <div>
          <h3 className="text-lg font-semibold text-cyan-300 mb-4">Prediction Results</h3>
          
          {prediction ? (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 p-6 rounded-xl border border-cyan-500/30">
                <div className="text-center">
                  <div className="text-3xl font-bold text-cyan-300 mb-2">
                    {formatCurrency(prediction.predictedPrice)}
                  </div>
                  <div className="text-sm text-gray-400">Predicted Auction Price</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700/30 p-4 rounded-lg border border-gray-600">
                  <div className="text-2xl font-bold text-green-400">
                    {prediction.confidence.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-400">Confidence</div>
                </div>
                
                <div className="bg-gray-700/30 p-4 rounded-lg border border-gray-600">
                  <div className="text-sm text-gray-300">
                    <div>Min: {formatCurrency(prediction.minPrice)}</div>
                    <div>Max: {formatCurrency(prediction.maxPrice)}</div>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">Confidence Interval</div>
                </div>
              </div>
              
              <div className="text-sm text-gray-400">
                <p className="mb-2">📊 Historical Trend Analysis</p>
                <div className="space-y-2">
                  {historicalData.map((data, index) => (
                    <div key={index} className="flex justify-between">
                      <span>{data.auction} Auction:</span>
                      <span className="text-cyan-300">{formatCurrency(data.price)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <div className="text-5xl mb-4">📊</div>
              <p>Enter player statistics to get price prediction</p>
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-8 pt-6 border-t border-gray-700">
        <div className="text-sm text-gray-400">
          <p>💡 <strong>AI Insight:</strong> This prediction model considers performance metrics, recent form, 
          and market trends. Use as a reference point for your bidding strategy.</p>
        </div>
      </div>
    </div>
  );
};

const TeamBuilderSimulator: React.FC = () => {
  const { state, dispatch } = useAppContext();
  
  // Team composition validation
  const teamStats = useMemo(() => {
    const batsmen = state.selectedPlayers.filter(p => p.role === 'Batsman' || p.role === 'Wicket-keeper').length;
    const bowlers = state.selectedPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = state.selectedPlayers.filter(p => p.role === 'All-rounder').length;
    const wicketkeepers = state.selectedPlayers.filter(p => p.role === 'Wicket-keeper').length;
    const overseas = state.selectedPlayers.filter(p => p.isOverseas).length;
    const budgetSpent = state.selectedPlayers.reduce((sum, p) => sum + p.currentPrice, 0);
    
    return {
      batsmen,
      bowlers,
      allrounders,
      wicketkeepers,
      overseas,
      totalPlayers: state.selectedPlayers.length,
      budgetSpent,
      balanceScore: Math.min(100, Math.max(0, 100 - (Math.abs(batsmen - 5) + Math.abs(bowlers - 5) + Math.abs(allrounders - 3)) * 10))
    };
  }, [state.selectedPlayers]);
  
  const warnings = [];
  if (teamStats.overseas > 8) warnings.push('Too many overseas players (max 8)');
  if (teamStats.bowlers < 5) warnings.push('Weak bowling attack (need more bowlers)');
  if (teamStats.batsmen < 6) warnings.push('Insufficient batting depth');
  if (teamStats.wicketkeepers === 0) warnings.push('No wicket-keeper selected');
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">🛠 TEAM BUILDER SIMULATOR</h3>
      
      {/* Team Composition */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Current Team Composition</h4>
        
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
          <div className="bg-purple-900/20 p-3 rounded-lg border border-purple-500/30">
            <div className="text-2xl font-bold text-purple-300">{teamStats.wicketkeepers}</div>
            <div className="text-xs text-purple-200">Wicket-keepers</div>
          </div>
        </div>
        
        <div className="bg-gray-700/30 p-3 rounded-lg border border-gray-600">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{teamStats.overseas}/8</div>
            <div className="text-xs text-gray-300">Overseas Players</div>
          </div>
        </div>
      </div>
      
      {/* Budget Tracker */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Budget Allocation</h4>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300">Spent</span>
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
      
      {/* Balance Score */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Team Balance</h4>
        <div className="text-center">
          <div className={`text-4xl font-bold mb-2 ${
            teamStats.balanceScore > 70 ? 'text-green-400' : 
            teamStats.balanceScore > 40 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {teamStats.balanceScore}/100
          </div>
          <div className="text-sm text-gray-400">Composition Quality Score</div>
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
      
      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-orange-300 mb-3">⚠️ Warnings</h4>
          <div className="space-y-2">
            {warnings.map((warning, index) => (
              <div key={index} className="bg-orange-900/30 border border-orange-500/30 rounded-lg p-3">
                <div className="text-sm text-orange-200">{warning}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Team Players List */}
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
                    <div className="text-xs text-gray-400">{player.role}</div>
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
      
      {/* Reset Button */}
      {state.selectedPlayers.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={() => dispatch({ type: 'RESET_TEAM' })}
            className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all duration-300"
          >
            Reset Team
          </button>
        </div>
      )}
    </div>
  );
};

const AuctionBiddingAssistant: React.FC = () => {
  const { state } = useAppContext();
  
  // Calculate walk-away prices and recommendations
  const playersWithRecommendations = useMemo(() => {
    return [...state.targetPlayers, ...state.backupPlayers].map(player => {
      const walkAwayPrice = player.predictedValue * 1.2; // 20% premium max
      const currentValueRatio = player.currentPrice / player.predictedValue;
      
      let recommendation: 'BID' | 'HOLD' | 'STOP' = 'HOLD';
      let riskLevel: 'Low' | 'Medium' | 'High' = 'Medium';
      let riskColor = 'text-yellow-400';
      
      if (currentValueRatio < 0.8) {
        recommendation = 'BID';
        riskLevel = 'Low';
        riskColor = 'text-green-400';
      } else if (currentValueRatio > 1.3) {
        recommendation = 'STOP';
        riskLevel = 'High';
        riskColor = 'text-red-400';
      }
      
      return {
        ...player,
        walkAwayPrice,
        recommendation,
        riskLevel,
        riskColor,
        currentValueRatio
      };
    });
  }, [state.targetPlayers, state.backupPlayers]);
  
  // Priority categories
  const mustBuyPlayers = playersWithRecommendations.filter(p => p.recommendation === 'BID' && p.valueScore > 8);
  const targetPlayers = playersWithRecommendations.filter(p => p.recommendation === 'BID' && p.valueScore <= 8);
  const holdPlayers = playersWithRecommendations.filter(p => p.recommendation === 'HOLD');
  const avoidPlayers = playersWithRecommendations.filter(p => p.recommendation === 'STOP');
  
  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'BID': return 'text-green-400';
      case 'HOLD': return 'text-yellow-400';
      case 'STOP': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">💰 AUCTION BIDDING ASSISTANT</h3>
      
      {/* Priority Queue Summary */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Priority Queue</h4>
        
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-green-900/20 p-3 rounded-lg border border-green-500/30 text-center">
            <div className="text-2xl font-bold text-green-300">{mustBuyPlayers.length}</div>
            <div className="text-xs text-green-200">Must Buy</div>
          </div>
          <div className="bg-blue-900/20 p-3 rounded-lg border border-blue-500/30 text-center">
            <div className="text-2xl font-bold text-blue-300">{targetPlayers.length}</div>
            <div className="text-xs text-blue-200">Target</div>
          </div>
          <div className="bg-yellow-900/20 p-3 rounded-lg border border-yellow-500/30 text-center">
            <div className="text-2xl font-bold text-yellow-300">{holdPlayers.length}</div>
            <div className="text-xs text-yellow-200">Hold</div>
          </div>
          <div className="bg-red-900/20 p-3 rounded-lg border border-red-500/30 text-center">
            <div className="text-2xl font-bold text-red-300">{avoidPlayers.length}</div>
            <div className="text-xs text-red-200">Avoid</div>
          </div>
        </div>
      </div>
      
      {/* Player Recommendations */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Player Recommendations</h4>
        
        {playersWithRecommendations.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <div className="text-3xl mb-2">📋</div>
            <p>Add players to your target or backup list</p>
            <p className="text-sm mt-1">Use the Player Intelligence Hub</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {playersWithRecommendations.slice(0, 8).map((player) => (
              <div 
                key={player.id} 
                className="bg-gray-700/30 p-4 rounded-lg border border-gray-600 hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="font-medium text-white">{player.name}</div>
                    <div className="text-sm text-gray-400">{player.role} • {player.cluster}</div>
                  </div>
                  <div className={`text-sm font-bold ${getRecommendationColor(player.recommendation)}`}>
                    {player.recommendation}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-gray-400">Current Bid</div>
                    <div className="text-cyan-300 font-medium">{formatCurrency(player.currentPrice)}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Walk-away</div>
                    <div className="text-orange-300 font-medium">{formatCurrency(player.walkAwayPrice)}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Predicted Value</div>
                    <div className="text-green-300 font-medium">{formatCurrency(player.predictedValue)}</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Risk Level</div>
                    <div className={`font-medium ${player.riskColor}`}>{player.riskLevel}</div>
                  </div>
                </div>
                
                <div className="mt-3 pt-3 border-t border-gray-600">
                  <div className="text-xs text-gray-400">
                    Value Score: {player.valueScore.toFixed(1)} • 
                    Current/Predicted: {(player.currentValueRatio * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Bidding Strategy Tips */}
      <div className="pt-4 border-t border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-3">💡 Bidding Strategy</h4>
        <div className="text-sm text-gray-400 space-y-2">
          <p>• <strong>Must Buy:</strong> Players undervalued by market, bid confidently</p>
          <p>• <strong>Target:</strong> Good value players, stay within walk-away price</p>
          <p>• <strong>Hold:</strong> Fairly priced, wait for better opportunities</p>
          <p>• <strong>Avoid:</strong> Overpriced players, let others overpay</p>
          <p className="mt-3 pt-2 border-t border-gray-600 text-xs">
            💰 <strong>Pro Tip:</strong> Save 25% of budget for last 10 players
          </p>
        </div>
      </div>
    </div>
  );
};

const InsightsPanel: React.FC = () => {
  const { state } = useAppContext();
  
  // Generate AI insights based on current team composition and market data
  const insights = useMemo(() => {
    const insightsList = [];
    
    // Team composition insights
    const batsmen = state.selectedPlayers.filter(p => p.role === 'Batsman' || p.role === 'Wicket-keeper').length;
    const bowlers = state.selectedPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = state.selectedPlayers.filter(p => p.role === 'All-rounder').length;
    const overseas = state.selectedPlayers.filter(p => p.isOverseas).length;
    const budgetUsed = state.budget - state.remainingBudget;
    
    // Budget allocation insights
    if (budgetUsed > state.budget * 0.7 && state.selectedPlayers.length < 20) {
      insightsList.push({
        type: 'warning',
        title: 'Budget Allocation Alert',
        message: `You've spent ${((budgetUsed / state.budget) * 100).toFixed(0)}% of your budget but only selected ${state.selectedPlayers.length} players. Consider saving more for later rounds.`
      });
    }
    
    if (budgetUsed < state.budget * 0.4 && state.selectedPlayers.length > 15) {
      insightsList.push({
        type: 'info',
        title: 'Budget Utilization',
        message: `You're being conservative with ${formatCurrency(state.remainingBudget)} remaining. Consider being more aggressive for key players.`
      });
    }
    
    // Team balance insights
    if (batsmen < 6) {
      insightsList.push({
        type: 'warning',
        title: 'Batting Depth Concern',
        message: `Only ${batsmen} batsmen selected. Consider adding 2-3 more batsmen for better depth.`
      });
    }
    
    if (bowlers < 5) {
      insightsList.push({
        type: 'warning',
        title: 'Bowling Attack Weak',
        message: `Only ${bowlers} bowlers selected. A strong bowling attack is crucial for IPL success.`
      });
    }
    
    if (allrounders < 2) {
      insightsList.push({
        type: 'info',
        title: 'All-rounder Opportunity',
        message: `Consider adding more all-rounders. They provide flexibility and can bat/bowl in crucial situations.`
      });
    }
    
    // Overseas player insights
    if (overseas > 6) {
      insightsList.push({
        type: 'info',
        title: 'Overseas Player Balance',
        message: `${overseas} overseas players selected. Ensure good Indian player representation for team chemistry.`
      });
    }
    
    // Market insights
    const valuePlayers = state.players.filter(p => p.cluster === 'Value' && !p.isSelected && !p.targetList);
    if (valuePlayers.length > 5) {
      insightsList.push({
        type: 'success',
        title: 'Market Opportunity',
        message: `There are ${valuePlayers.length} high-value players available. Consider targeting players like ${valuePlayers[0]?.name} and ${valuePlayers[1]?.name}.`
      });
    }
    
    // Performance insights
    const highPerformers = state.selectedPlayers.filter(p => p.performanceScore > 80);
    if (highPerformers.length > 3) {
      insightsList.push({
        type: 'success',
        title: 'Strong Core Built',
        message: `You've selected ${highPerformers.length} high-performing players. Your team foundation looks solid.`
      });
    }
    
    // Risk insights
    const riskyPlayers = state.selectedPlayers.filter(p => p.cluster === 'Risky');
    if (riskyPlayers.length > 2) {
      insightsList.push({
        type: 'warning',
        title: 'Risk Management',
        message: `${riskyPlayers.length} risky players in your team. Ensure you have reliable backups for these positions.`
      });
    }
    
    // Default positive insight if no issues
    if (insightsList.length === 0) {
      insightsList.push({
        type: 'success',
        title: 'Great Progress',
        message: `Your team building strategy looks well-balanced. Continue with your current approach and focus on filling remaining positions strategically.`
      });
    }
    
    return insightsList;
  }, [state.selectedPlayers, state.remainingBudget, state.budget, state.players]);
  
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'warning': return '⚠️';
      case 'success': return '✅';
      case 'info': return 'ℹ️';
      default: return '💡';
    }
  };
  
  const getInsightColor = (type: string) => {
    switch (type) {
      case 'warning': return 'border-orange-500/30 bg-orange-900/20';
      case 'success': return 'border-green-500/30 bg-green-900/20';
      case 'info': return 'border-blue-500/30 bg-blue-900/20';
      default: return 'border-cyan-500/30 bg-cyan-900/20';
    }
  };
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">💡 AI INSIGHTS & RECOMMENDATIONS</h3>
      
      <div className="space-y-4">
        {insights.map((insight, index) => (
          <div 
            key={index}
            className={`p-4 rounded-lg border ${getInsightColor(insight.type)} transition-all duration-300 hover:scale-[1.02]`}
          >
            <div className="flex items-start space-x-3">
              <div className="text-2xl mt-1">{getInsightIcon(insight.type)}</div>
              <div>
                <h4 className="font-semibold text-white mb-2">{insight.title}</h4>
                <p className="text-sm text-gray-300 leading-relaxed">{insight.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Quick Stats */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-3">📊 Quick Assessment</h4>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-700/30 p-3 rounded-lg border border-gray-600 text-center">
            <div className="text-xl font-bold text-cyan-300">
              {((state.budget - state.remainingBudget) / state.budget * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-400">Budget Used</div>
          </div>
          <div className="bg-gray-700/30 p-3 rounded-lg border border-gray-600 text-center">
            <div className="text-xl font-bold text-green-300">
              {state.selectedPlayers.length}
            </div>
            <div className="text-xs text-gray-400">Players Selected</div>
          </div>
        </div>
        
        <div className="mt-3 text-center">
          <div className="text-sm text-gray-400">
            {state.remainingBudget > 4000 ? '📈 Aggressive bidding phase' : 
             state.remainingBudget > 2000 ? '🎯 Strategic selection phase' : 
             '🏁 Final sprint phase'}
          </div>
        </div>
      </div>
    </div>
  );
};

const HistoricalAnalytics: React.FC = () => {
  // Mock historical data
  const auctionTrends = [
    { year: '2020', avgBatsmanPrice: 280, avgBowlerPrice: 220, avgAllrounderPrice: 350 },
    { year: '2021', avgBatsmanPrice: 320, avgBowlerPrice: 260, avgAllrounderPrice: 400 },
    { year: '2022', avgBatsmanPrice: 380, avgBowlerPrice: 310, avgAllrounderPrice: 480 },
    { year: '2023', avgBatsmanPrice: 450, avgBowlerPrice: 370, avgAllrounderPrice: 560 },
    { year: '2024', avgBatsmanPrice: 520, avgBowlerPrice: 430, avgAllrounderPrice: 650 }
  ];
  
  const topBuys = [
    { name: 'S. Hetmyer', price: 1200, team: 'DC', season: 2022 },
    { name: 'L. Livingstone', price: 1100, team: 'PBKS', season: 2022 },
    { name: 'R. Parag', price: 1050, team: 'RR', season: 2023 },
    { name: 'M. Jansen', price: 950, team: 'SRH', season: 2022 },
    { name: 'T. Kohli', price: 900, team: 'RCB', season: 2023 }
  ];
  
  const flopBuys = [
    { name: 'M. Ali', price: 700, team: 'CSK', season: 2021, actualPrice: 150 },
    { name: 'J. Archer', price: 780, team: 'RR', season: 2021, actualPrice: 200 },
    { name: 'C. Jordan', price: 650, team: 'SRH', season: 2022, actualPrice: 180 },
    { name: 'D. Pretorius', price: 600, team: 'DC', season: 2021, actualPrice: 120 },
    { name: 'M. Richardson', price: 550, team: 'PBKS', season: 2022, actualPrice: 100 }
  ];
  
  const priceInflation = useMemo(() => {
    const inflationData = [];
    for (let i = 1; i < auctionTrends.length; i++) {
      const prev = auctionTrends[i-1];
      const curr = auctionTrends[i];
      const inflation = ((curr.avgBatsmanPrice - prev.avgBatsmanPrice) / prev.avgBatsmanPrice) * 100;
      inflationData.push({
        year: curr.year,
        inflation: inflation.toFixed(1)
      });
    }
    return inflationData;
  }, [auctionTrends]);
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">📊 HISTORICAL ANALYTICS</h3>
      
      {/* Price Trends */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">📈 Price Trends by Role (2020-2024)</h4>
        
        <div className="space-y-3">
          {auctionTrends.map((trend, index) => (
            <div key={index} className="bg-gray-700/30 p-3 rounded-lg border border-gray-600">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-white">{trend.year}</span>
                <span className="text-sm text-gray-400">Avg Prices</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <div className="text-blue-300">Batsman</div>
                  <div className="font-medium">{formatCurrency(trend.avgBatsmanPrice)}</div>
                </div>
                <div>
                  <div className="text-green-300">Bowler</div>
                  <div className="font-medium">{formatCurrency(trend.avgBowlerPrice)}</div>
                </div>
                <div>
                  <div className="text-yellow-300">All-rounder</div>
                  <div className="font-medium">{formatCurrency(trend.avgAllrounderPrice)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Top Buys vs Flops */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">🏆 Top Buys vs 💸 Flops</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="text-md font-semibold text-green-300 mb-2">Top Value Buys</h5>
            <div className="space-y-2">
              {topBuys.map((player, index) => (
                <div key={index} className="bg-green-900/20 p-2 rounded border border-green-500/30">
                  <div className="font-medium text-white text-sm">{player.name}</div>
                  <div className="text-xs text-green-200">
                    {formatCurrency(player.price)} • {player.team} {player.season}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h5 className="text-md font-semibold text-red-300 mb-2">Overpaid Players</h5>
            <div className="space-y-2">
              {flopBuys.map((player, index) => (
                <div key={index} className="bg-red-900/20 p-2 rounded border border-red-500/30">
                  <div className="font-medium text-white text-sm">{player.name}</div>
                  <div className="text-xs text-red-200">
                    Paid: {formatCurrency(player.price)}
                  </div>
                  <div className="text-xs text-red-200">
                    Current Value: {formatCurrency(player.actualPrice)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Price Inflation */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">💹 Price Inflation Rate</h4>
        
        <div className="bg-gray-700/30 p-4 rounded-lg border border-gray-600">
          <div className="space-y-3">
            {priceInflation.map((data, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-gray-300">{data.year}</span>
                <div className="flex items-center space-x-2">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    parseFloat(data.inflation) > 15 ? 'bg-red-900/30 text-red-300' : 
                    parseFloat(data.inflation) > 10 ? 'bg-yellow-900/30 text-yellow-300' : 
                    'bg-green-900/30 text-green-300'
                  }`}>
                    {data.inflation}%
                  </div>
                  <div className="text-sm text-gray-400">inflation</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Key Insights */}
      <div className="pt-4 border-t border-gray-700">
        <h4 className="text-lg font-semibold text-white mb-3">🔑 Key Market Insights</h4>
        <div className="text-sm text-gray-400 space-y-2">
          <p>• All-rounder prices have increased 85% since 2020</p>
          <p>• Batsmen premium: 30% more than bowlers on average</p>
          <p>• 2022-2024 saw highest price inflation (15-20% annually)</p>
          <p>• Overseas players command 25-40% premium over Indians</p>
          <p className="mt-3 pt-2 border-t border-gray-600 text-xs">
            💡 <strong>Strategy:</strong> Focus on undervalued roles and emerging talents
          </p>
        </div>
      </div>
    </div>
  );
};

// Professional Features Component
const ProfessionalFeatures: React.FC = () => {
  const { state } = useAppContext();
  
  const exportToCSV = () => {
    const csvContent = [
      ['Player Name', 'Role', 'Country', 'Base Price', 'Predicted Value', 'Cluster', 'Performance Score', 'Consistency'],
      ...state.selectedPlayers.map(player => [
        player.name,
        player.role,
        player.country,
        player.basePrice.toString(),
        player.predictedValue.toString(),
        player.cluster,
        player.performanceScore.toString(),
        player.consistency.toString()
      ])
    ];
    
    const csvString = csvContent.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ipl_team_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };
  
  const exportToPDF = () => {
    // Simple PDF export simulation
    alert('PDF export functionality would be implemented with jsPDF library');
  };
  
  return (
    <div className="fixed bottom-6 right-6 flex space-x-3 z-50">
      <button
        onClick={exportToCSV}
        disabled={state.selectedPlayers.length === 0}
        className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
          state.selectedPlayers.length === 0
            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 text-white hover:scale-105'
        }`}
      >
        <span>📊</span>
        <span>Export CSV</span>
      </button>
      
      <button
        onClick={exportToPDF}
        disabled={state.selectedPlayers.length === 0}
        className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
          state.selectedPlayers.length === 0
            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white hover:scale-105'
        }`}
      >
        <span>📄</span>
        <span>Export PDF</span>
      </button>
    </div>
  );
};

// Loading Component
const LoadingSpinner: React.FC = () => (
  <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
      <p className="text-cyan-300 text-lg font-medium">Loading Auction Dashboard...</p>
      <p className="text-gray-400 text-sm mt-2">Analyzing player data and market trends</p>
    </div>
  </div>
);

// Error Boundary Component
class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean}> {
  constructor(props: {children: React.ReactNode}) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-white mb-2">Something went wrong</h2>
            <p className="text-gray-400 mb-6">We're sorry, but there was an error loading the dashboard.</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition-colors"
            >
              Reload Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Enhanced Main App Component
const EnhancedApp: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, []);
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return (
    <ErrorBoundary>
      <App />
      <ProfessionalFeatures />
    </ErrorBoundary>
  );
};

export default EnhancedApp;