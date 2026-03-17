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

// ==================== MOCK DATA GENERATION ====================

const generateMockPlayers = (): Player[] => {
  const firstNames = ['Virat', 'Rohit', 'Shikhar', 'KL', 'Shreyas', 'Rishabh', 'Hardik', 'Jasprit', 'Mohammed', 'Ravindra'];
  const lastNames = ['Kohli', 'Sharma', 'Dhawan', 'Rahul', 'Iyer', 'Pant', 'Pandya', 'Bumrah', 'Shami', 'Jadeja'];
  const countries = ['India', 'Australia', 'England', 'South Africa'];
  const roles: ('Batsman' | 'Bowler' | 'All-rounder' | 'Wicket-keeper')[] = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const clusters: ('Elite' | 'Good' | 'Value' | 'Risky')[] = ['Elite', 'Good', 'Value', 'Risky'];
  
  const players: Player[] = [];
  const totalPlayers = 50; // Reduced for testing
  
  for (let i = 0; i < totalPlayers; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const name = `${firstName} ${lastName}`;
    const role = roles[Math.floor(Math.random() * roles.length)];
    const country = countries[Math.floor(Math.random() * countries.length)];
    const cluster = clusters[Math.floor(Math.random() * clusters.length)];
    
    let runs = 0, strikeRate = 0, wickets = 0, economy = 0;
    
    if (role === 'Batsman' || role === 'Wicket-keeper') {
      runs = Math.floor(Math.random() * 3000) + 500;
      strikeRate = Math.random() * 50 + 120;
    } else if (role === 'Bowler') {
      wickets = Math.floor(Math.random() * 100) + 20;
      economy = Math.random() * 2 + 7;
    } else {
      runs = Math.floor(Math.random() * 2000) + 300;
      strikeRate = Math.random() * 40 + 110;
      wickets = Math.floor(Math.random() * 60) + 10;
      economy = Math.random() * 3 + 8;
    }
    
    const matches = Math.floor(Math.random() * 100) + 20;
    const basePrice = Math.floor(Math.random() * 1500) + 200;
    const performanceScore = (runs / 100) + (wickets * 2) + (matches * 0.5);
    const consistency = Math.random() * 100;
    const recentForm = Math.random() * 100;
    const predictedValue = basePrice * (0.8 + Math.random() * 0.8);
    const valueScore = performanceScore / (predictedValue / 100);
    
    players.push({
      id: `player_${i}`,
      name,
      role,
      country,
      experience: 'Experienced',
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
    const mockPlayers = generateMockPlayers();
    setState(prev => ({ ...prev, players: mockPlayers }));
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
            <p className="text-cyan-200 mt-1">Professional Strategy Dashboard</p>
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
  
  return (
    <div className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 backdrop-blur-sm rounded-2xl p-8 border border-cyan-500/30 shadow-2xl">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">🎯 SMART AUCTION COMMAND CENTER</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-800/30 rounded-xl p-6 border border-blue-500/30">
          <div className="text-3xl font-bold text-white mb-2">{state.selectedPlayers.length}/25</div>
          <div className="text-blue-200">Players Selected</div>
          <div className="w-full bg-blue-900/50 rounded-full h-2 mt-3">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(state.selectedPlayers.length / 25) * 100}%` }}
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
          <div className="text-3xl font-bold text-white mb-2">{25 - state.selectedPlayers.length}</div>
          <div className="text-orange-200">Slots to Fill</div>
        </div>
      </div>
    </div>
  );
};

// Player Intelligence Hub
const PlayerIntelligenceHub: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredPlayers = useMemo(() => {
    return state.players.filter(player => 
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      player.country.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [state.players, searchTerm]);
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-300 mb-6">📊 PLAYER INTELLIGENCE HUB</h2>
      
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search players..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Player</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Role</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Stats</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Value</th>
              <th className="px-4 py-3 text-cyan-300 font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {filteredPlayers.slice(0, 8).map((player) => (
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
                  </div>
                </td>
                <td className="px-4 py-3">
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Team Builder
const TeamBuilderSimulator: React.FC = () => {
  const { state, dispatch } = useAppContext();
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-cyan-300 mb-4">🛠 TEAM BUILDER SIMULATOR</h3>
      
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-white mb-3">Selected Players ({state.selectedPlayers.length})</h4>
        
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
                className="flex justify-between items-center bg-gray-700/30 p-3 rounded-lg border border-gray-600"
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
    </div>
  );
};

// Main App Component
const WorkingApp: React.FC = () => {
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

export default WorkingApp;