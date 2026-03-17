import React, { useState, useEffect, createContext, useContext, useReducer } from 'react';

// Types
interface Player {
  id: string;
  name: string;
  fullName: string;
  team: string;
  role: string;
  basePrice: number;
  currentPrice: number;
  predictedValue: number;
  valueScore: number;
  runs: number;
  wickets: number;
  strikeRate: number;
  economy: number;
  matches: number;
  cluster: string;
  imageUrl: string;
  overseas: boolean;
}

interface AppState {
  players: Player[];
  selectedPlayers: Player[];
  preparedTeams: Record<string, Player[]>;
  isLoading: boolean;
  error: string | null;
}

// Action Types
type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'SET_PLAYERS'; payload: Player[] }
  | { type: 'SELECT_PLAYER'; payload: Player }
  | { type: 'REMOVE_PLAYER'; payload: string }
  | { type: 'UPDATE_PREPARED_TEAMS'; payload: Record<string, Player[]> }
  | { type: 'ADD_TO_TEAM'; payload: { team: string; player: Player } }
  | { type: 'REMOVE_FROM_TEAM'; payload: { team: string; playerId: string } }
  | { type: 'RESET_TEAM'; payload: string };

// Reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_PLAYERS':
      return { ...state, players: action.payload, isLoading: false, error: null };
    case 'SELECT_PLAYER':
      return { ...state, selectedPlayers: [...state.selectedPlayers, action.payload] };
    case 'REMOVE_PLAYER':
      return { ...state, selectedPlayers: state.selectedPlayers.filter(p => p.id !== action.payload) };
    case 'UPDATE_PREPARED_TEAMS':
      return { ...state, selectedPlayers: [], preparedTeams: action.payload };
    case 'ADD_TO_TEAM':
      const { team: teamName, player } = action.payload;
      const currentTeam = state.preparedTeams[teamName] || [];
      if (!currentTeam.some(p => p.id === player.id)) {
        return {
          ...state,
          preparedTeams: {
            ...state.preparedTeams,
            [teamName]: [...currentTeam, player]
          }
        };
      }
      return state;
    case 'REMOVE_FROM_TEAM':
      const { team: removeTeam, playerId } = action.payload;
      return {
        ...state,
        preparedTeams: {
          ...state.preparedTeams,
          [removeTeam]: (state.preparedTeams[removeTeam] || []).filter(p => p.id !== playerId)
        }
      };
    case 'RESET_TEAM':
      const newTeams = { ...state.preparedTeams };
      delete newTeams[action.payload];
      return { ...state, preparedTeams: newTeams };
    default:
      return state;
  }
};

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

// Data Loader
const fetchPlayersData = async (): Promise<Player[]> => {
  try {
    console.log('Attempting to fetch player data...');
    const response = await fetch('/dashboard_players.json');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Raw data received:', data.length, 'players');
    
    // Check if it's an array or object with players array
    const playersArray = Array.isArray(data) ? data : data.players || [];
    
    if (playersArray.length === 0) {
      throw new Error('No player data found');
    }
    
    const mappedPlayers = playersArray.map((player: any, index: number) => ({
      id: player.id || `player_${index + 1}`,
      name: player.name || player.player || 'Unknown Player',
      fullName: player.full_name || player.name || 'Unknown Player',
      team: player.team || 'TBD',
      role: player.role || 'All-rounder',
      basePrice: player.base_price || player.price || 0,
      currentPrice: player.current_price || player.price || 0,
      predictedValue: player.predicted_value || player.price || 0,
      valueScore: player.value_score || 50,
      runs: player.runs || player.total_runs || 0,
      wickets: player.wickets || player.total_wickets || 0,
      strikeRate: player.strike_rate || 0,
      economy: player.economy || 0,
      matches: player.matches || player.matches_played || 0,
      cluster: player.cluster || 'Developing',
      imageUrl: player.image_url || 'https://via.placeholder.com/150',
      overseas: player.overseas || false,
    }));
    
    console.log('Mapped players:', mappedPlayers.length);
    return mappedPlayers;
  } catch (error) {
    console.error('Error fetching player data:', error);
    // Try alternative data sources
    try {
      const backupResponse = await fetch('dashboard_players.json');
      if (backupResponse.ok) {
        const backupData = await backupResponse.json();
        const backupPlayers = Array.isArray(backupData) ? backupData : backupData.players || [];
        return backupPlayers.map((player: any, index: number) => ({
          id: player.id || `player_${index + 1}`,
          name: player.name || 'Unknown Player',
          fullName: player.name || 'Unknown Player',
          team: player.team || 'TBD',
          role: player.role || 'All-rounder',
          basePrice: player.price || 0,
          currentPrice: player.price || 0,
          predictedValue: player.price || 0,
          valueScore: 50,
          runs: player.runs || 0,
          wickets: player.wickets || 0,
          strikeRate: player.strike_rate || 0,
          economy: player.economy || 0,
          matches: player.matches || 0,
          cluster: 'Developing',
          imageUrl: 'https://via.placeholder.com/150',
          overseas: false,
        }));
      }
    } catch (backupError) {
      console.error('Backup data fetch also failed:', backupError);
    }
    throw new Error('Failed to load player data from all sources');
  }
};

// Helper Functions
const formatCurrency = (amount: number): string => {
  return `₹${(amount / 100).toFixed(1)} Cr`;
};

const getClusterColor = (cluster: string): string => {
  const colors: Record<string, string> = {
    'Mega Star': 'bg-yellow-500',
    'Star': 'bg-blue-500',
    'Solid': 'bg-green-500',
    'Promising': 'bg-purple-500',
    'Developing': 'bg-gray-500',
  };
  return colors[cluster] || 'bg-gray-500';
};

const getBudgetRangeColor = (range: string): string => {
  switch (range) {
    case '₹15+ Cr': return 'bg-purple-500';
    case '₹10-15 Cr': return 'bg-blue-500';
    case '₹5-10 Cr': return 'bg-green-500';
    case '₹2-5 Cr': return 'bg-yellow-500';
    case '₹0-2 Cr': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

// App Provider
const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, {
    players: [],
    selectedPlayers: [],
    preparedTeams: {},
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        dispatch({ type: 'SET_LOADING', payload: true });
        const players = await fetchPlayersData();
        console.log('Players loaded:', players.length);
        if (players.length > 0) {
          dispatch({ type: 'SET_PLAYERS', payload: players });
        } else {
          throw new Error('No players found in data');
        }
      } catch (error) {
        console.error('Data loading failed:', error);
        // Generate sample data as fallback
        const samplePlayers: Player[] = [
          {
            id: 'player_1',
            name: 'Virat Kohli',
            fullName: 'Virat Kohli',
            team: 'RCB',
            role: 'Batsman',
            basePrice: 1700,
            currentPrice: 1700,
            predictedValue: 1800,
            valueScore: 95,
            runs: 7500,
            wickets: 0,
            strikeRate: 185.2,
            economy: 0,
            matches: 350,
            cluster: 'Mega Star',
            imageUrl: 'https://via.placeholder.com/150?text=VK',
            overseas: false
          },
          {
            id: 'player_2',
            name: 'Jasprit Bumrah',
            fullName: 'Jasprit Bumrah',
            team: 'MI',
            role: 'Bowler',
            basePrice: 1500,
            currentPrice: 1500,
            predictedValue: 1600,
            valueScore: 88,
            runs: 150,
            wickets: 180,
            strikeRate: 85.5,
            economy: 4.2,
            matches: 150,
            cluster: 'Star',
            imageUrl: 'https://via.placeholder.com/150?text=JB',
            overseas: false
          },
          {
            id: 'player_3',
            name: 'Andre Russell',
            fullName: 'Andre Russell',
            team: 'KKR',
            role: 'All-rounder',
            basePrice: 1400,
            currentPrice: 1400,
            predictedValue: 1500,
            valueScore: 85,
            runs: 4500,
            wickets: 160,
            strikeRate: 188.9,
            economy: 7.8,
            matches: 180,
            cluster: 'Star',
            imageUrl: 'https://via.placeholder.com/150?text=AR',
            overseas: true
          },
          {
            id: 'player_4',
            name: 'Rishabh Pant',
            fullName: 'Rishabh Pant',
            team: 'DC',
            role: 'Wicket-keeper',
            basePrice: 1200,
            currentPrice: 1200,
            predictedValue: 1300,
            valueScore: 82,
            runs: 3800,
            wickets: 0,
            strikeRate: 155.7,
            economy: 0,
            matches: 140,
            cluster: 'Solid',
            imageUrl: 'https://via.placeholder.com/150?text=RP',
            overseas: false
          },
          {
            id: 'player_5',
            name: 'David Warner',
            fullName: 'David Warner',
            team: 'DC',
            role: 'Batsman',
            basePrice: 1300,
            currentPrice: 1300,
            predictedValue: 1400,
            valueScore: 87,
            runs: 6200,
            wickets: 0,
            strikeRate: 175.3,
            economy: 0,
            matches: 300,
            cluster: 'Star',
            imageUrl: 'https://via.placeholder.com/150?text=DW',
            overseas: true
          }
        ];
        
        console.log('Using sample data with', samplePlayers.length, 'players');
        dispatch({ type: 'SET_PLAYERS', payload: samplePlayers });
      }
    };
    loadData();
  }, []);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// Team Preparation Section Component
const TeamPreparationSection: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [selectedTeam, setSelectedTeam] = useState('');
  const [showTeamPrep, setShowTeamPrep] = useState(false);
  const teamBudget = 12000; // 120 crore in lakhs

  const teams = ['CSK', 'MI', 'RCB', 'KKR', 'DC', 'PBKS', 'RR', 'SRH', 'GT', 'LSG'];

  const startTeamPreparation = (team: string) => {
    setSelectedTeam(team);
    setShowTeamPrep(true);
  };

  const addToTeam = (player: Player) => {
    if (!selectedTeam) return;
    
    const currentTeam = state.preparedTeams[selectedTeam] || [];
    if (currentTeam.some((p: Player) => p.id === player.id)) return;
    
    const newTeam = [...currentTeam, player];
    const totalSpent = newTeam.reduce((sum: number, p: Player) => sum + p.currentPrice, 0);
    
    if (totalSpent <= teamBudget) {
      dispatch({ type: 'ADD_TO_TEAM', payload: { team: selectedTeam, player } });
    } else {
      alert(`Budget exceeded! Current team total: ${formatCurrency(totalSpent)}`);
    }
  };

  const removeFromTeam = (playerId: string) => {
    if (!selectedTeam) return;
    dispatch({ type: 'REMOVE_FROM_TEAM', payload: { team: selectedTeam, playerId } });
  };

  const finishTeamPreparation = () => {
    if (!selectedTeam) return;
    
    const teamPlayers = state.preparedTeams[selectedTeam] || [];
    const totalSpent = teamPlayers.reduce((sum: number, p: Player) => sum + p.currentPrice, 0);
    
    if (totalSpent > teamBudget) {
      alert(`Budget exceeded! Total: ${formatCurrency(totalSpent)}`);
      return;
    }
    
    dispatch({ 
      type: 'UPDATE_PREPARED_TEAMS', 
      payload: state.preparedTeams
    });
    
    setShowTeamPrep(false);
    setSelectedTeam('');
    
    // Check if we have 2+ teams for auto-comparison
    const teamCount = Object.keys(state.preparedTeams).length;
    if (teamCount >= 2) {
      alert(`Team ${selectedTeam} prepared successfully! ${teamCount} teams ready for comparison.`);
    }
  };

  const cancelTeamPreparation = () => {
    setShowTeamPrep(false);
    setSelectedTeam('');
  };

  const resetTeam = (team: string) => {
    dispatch({ type: 'RESET_TEAM', payload: team });
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center">
        <span className="mr-3">🏏</span>
        Team Preparation
      </h2>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {teams.map(team => {
          const teamPlayers = state.preparedTeams[team] || [];
          const totalSpent = teamPlayers.reduce((sum: number, p: Player) => sum + p.currentPrice, 0);
          const isPrepared = teamPlayers.length > 0;
          
          return (
            <div key={team} className="relative">
              <button
                onClick={() => startTeamPreparation(team)}
                disabled={showTeamPrep && selectedTeam !== team}
                className={`w-full p-4 rounded-lg border-2 transition-all ${
                  showTeamPrep && selectedTeam === team
                    ? 'border-cyan-500 bg-cyan-500/20'
                    : isPrepared
                    ? 'border-green-500 bg-green-500/20 hover:border-green-400'
                    : 'border-gray-600 bg-gray-700/50 hover:border-gray-500'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="font-bold text-lg text-white">{team}</div>
                <div className="text-sm text-gray-300 mt-1">
                  {teamPlayers.length} players
                </div>
                <div className="text-xs text-cyan-400 mt-1">
                  {formatCurrency(totalSpent)} / ₹120 Cr
                </div>
                {isPrepared && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </button>
              
              {isPrepared && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    resetTeam(team);
                  }}
                  className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-red-500 hover:bg-red-600 text-white text-xs px-2 py-1 rounded-full transition-colors"
                >
                  Reset
                </button>
              )}
            </div>
          );
        })}
      </div>

      {showTeamPrep && (
        <div className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-white">
              Preparing Team: <span className="text-cyan-400">{selectedTeam}</span>
            </h3>
            <div className="text-right">
              <div className="text-sm text-gray-300">Budget Remaining</div>
              <div className="text-lg font-bold text-green-400">
                {formatCurrency(teamBudget - (state.preparedTeams[selectedTeam] || []).reduce((sum: number, p: Player) => sum + p.currentPrice, 0))}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Selected Players ({(state.preparedTeams[selectedTeam] || []).length})</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {(state.preparedTeams[selectedTeam] || []).map((player: Player) => (
                  <div key={player.id} className="flex justify-between items-center bg-gray-600/50 p-3 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <img 
                        src={player.imageUrl} 
                        alt={player.name}
                        className="w-8 h-8 rounded-full border border-cyan-500"
                      />
                      <div>
                        <div className="font-medium text-white text-sm">{player.name}</div>
                        <div className="text-xs text-gray-400">{player.role} • {player.team}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-cyan-400 font-medium text-sm">{formatCurrency(player.currentPrice)}</div>
                      <button
                        onClick={() => removeFromTeam(player.id)}
                        className="text-red-400 hover:text-red-300 text-xs mt-1"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
                {(state.preparedTeams[selectedTeam] || []).length === 0 && (
                  <div className="text-gray-400 text-center py-8">
                    No players selected yet
                  </div>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Team Summary</h4>
              <div className="bg-gray-600/30 rounded-lg p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Players:</span>
                  <span className="text-white font-medium">{(state.preparedTeams[selectedTeam] || []).length}/11</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Spent:</span>
                  <span className="text-cyan-400 font-medium">
                    {formatCurrency((state.preparedTeams[selectedTeam] || []).reduce((sum: number, p: Player) => sum + p.currentPrice, 0))}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Budget Remaining:</span>
                  <span className="text-green-400 font-medium">
                    {formatCurrency(teamBudget - (state.preparedTeams[selectedTeam] || []).reduce((sum: number, p: Player) => sum + p.currentPrice, 0))}
                  </span>
                </div>
                <div className="pt-3 border-t border-gray-600">
                  <div className="text-sm text-gray-400 mb-2">Role Distribution:</div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span>Batsmen:</span>
                      <span className="text-white">
                        {(state.preparedTeams[selectedTeam] || []).filter((p: Player) => p.role === 'Batsman').length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Bowlers:</span>
                      <span className="text-white">
                        {(state.preparedTeams[selectedTeam] || []).filter((p: Player) => p.role === 'Bowler').length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>All-rounders:</span>
                      <span className="text-white">
                        {(state.preparedTeams[selectedTeam] || []).filter((p: Player) => p.role === 'All-rounder').length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Wicket-keepers:</span>
                      <span className="text-white">
                        {(state.preparedTeams[selectedTeam] || []).filter((p: Player) => p.role === 'Wicket-keeper').length}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex space-x-3 mt-6">
            <button
              onClick={finishTeamPreparation}
              disabled={(state.preparedTeams[selectedTeam] || []).length === 0}
              className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded text-sm font-medium transition-colors disabled:cursor-not-allowed"
            >
              Finish Team
            </button>
            <button
              onClick={cancelTeamPreparation}
              className="flex-1 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Player Intelligence Hub
const PlayerIntelligenceHub: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [teamFilter, setTeamFilter] = useState('All');
  const [clusterFilter, setClusterFilter] = useState('All');
  const [overseasFilter, setOverseasFilter] = useState('All');
  const [budgetRange, setBudgetRange] = useState('All');
  const [selectedTeam, setSelectedTeam] = useState('');
  
  // Filter presets
  const budgetRanges = ['All', '₹15+ Cr', '₹10-15 Cr', '₹5-10 Cr', '₹2-5 Cr', '₹0-2 Cr'];
  const roles = ['All', 'Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'];
  const teams = ['All', 'CSK', 'MI', 'RCB', 'KKR', 'DC', 'PBKS', 'RR', 'SRH', 'GT', 'LSG'];
  const clusters = ['All', 'Mega Star', 'Star', 'Solid', 'Promising', 'Developing'];
  const overseasOptions = ['All', 'Indian', 'Overseas'];

  const addToTeam = (player: Player) => {
    if (!selectedTeam) return;
    
    const currentTeam = state.preparedTeams[selectedTeam] || [];
    if (currentTeam.some((p: Player) => p.id === player.id)) return;
    
    const newTeam = [...currentTeam, player];
    const totalSpent = newTeam.reduce((sum: number, p: Player) => sum + p.currentPrice, 0);
    
    if (totalSpent <= 12000) {
      dispatch({ type: 'ADD_TO_TEAM', payload: { team: selectedTeam, player } });
    } else {
      alert(`Budget exceeded! Current team total: ${formatCurrency(totalSpent)}`);
    }
  };

  const getBudgetRange = (price: number): string => {
    const crore = price / 100;
    if (crore >= 15) return '₹15+ Cr';
    if (crore >= 10) return '₹10-15 Cr';
    if (crore >= 5) return '₹5-10 Cr';
    if (crore >= 2) return '₹2-5 Cr';
    return '₹0-2 Cr';
  };

  const filteredPlayers = state.players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         player.team.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'All' || player.role === roleFilter;
    const matchesTeam = teamFilter === 'All' || player.team === teamFilter;
    const matchesCluster = clusterFilter === 'All' || player.cluster === clusterFilter;
    const matchesOverseas = overseasFilter === 'All' || 
                           (overseasFilter === 'Indian' && !player.overseas) ||
                           (overseasFilter === 'Overseas' && player.overseas);
    const matchesBudget = budgetRange === 'All' || getBudgetRange(player.currentPrice) === budgetRange;
    
    return matchesSearch && matchesRole && matchesTeam && matchesCluster && matchesOverseas && matchesBudget;
  });

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-400 mb-6 flex items-center">
        <span className="mr-3">📊</span>
        Player Intelligence Hub
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Player or team..."
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {roles.map(role => (
              <option key={role} value={role} className="bg-gray-800">{role}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Team</label>
          <select
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {teams.map(team => (
              <option key={team} value={team} className="bg-gray-800">{team}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Cluster</label>
          <select
            value={clusterFilter}
            onChange={(e) => setClusterFilter(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {clusters.map(cluster => (
              <option key={cluster} value={cluster} className="bg-gray-800">{cluster}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Overseas</label>
          <select
            value={overseasFilter}
            onChange={(e) => setOverseasFilter(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {overseasOptions.map(option => (
              <option key={option} value={option} className="bg-gray-800">{option}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Budget Range</label>
          <select
            value={budgetRange}
            onChange={(e) => setBudgetRange(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {budgetRanges.map(range => (
              <option key={range} value={range} className="bg-gray-800">{range}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {['CSK', 'MI', 'RCB', 'KKR', 'DC', 'PBKS', 'RR', 'SRH', 'GT', 'LSG'].map(team => (
          <button
            key={team}
            onClick={() => setSelectedTeam(selectedTeam === team ? '' : team)}
            className={`px-3 py-2 rounded-lg border-2 transition-all ${
              selectedTeam === team
                ? 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
                : 'border-gray-600 bg-gray-700/50 text-gray-300 hover:border-gray-500'
            }`}
          >
            {team}
          </button>
        ))}
      </div>

      <div className="pt-4 border-t border-gray-600">
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-400">Active Filters:</span>
          {teamFilter !== 'All' && (
            <span className="px-2 py-1 bg-cyan-600/30 text-cyan-300 rounded text-sm">Team: {teamFilter}</span>
          )}
          {roleFilter !== 'All' && (
            <span className="px-2 py-1 bg-blue-600/30 text-blue-300 rounded text-sm">Role: {roleFilter}</span>
          )}
          {clusterFilter !== 'All' && (
            <span className="px-2 py-1 bg-purple-600/30 text-purple-300 rounded text-sm">Cluster: {clusterFilter}</span>
          )}
          {overseasFilter !== 'All' && (
            <span className="px-2 py-1 bg-green-600/30 text-green-300 rounded text-sm">Overseas: {overseasFilter}</span>
          )}
          {budgetRange !== 'All' && (
            <span className="px-2 py-1 bg-yellow-600/30 text-yellow-300 rounded text-sm">Budget: {budgetRange}</span>
          )}
          {searchTerm && (
            <span className="px-2 py-1 bg-red-600/30 text-red-300 rounded text-sm">Search: "{searchTerm}"</span>
          )}
        </div>
      </div>

      <div className="overflow-x-auto mt-6">
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
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getClusterColor(player.cluster)} text-white`}>
                    {player.cluster}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex space-x-1">
                    <button
                      onClick={() => {
                        if (selectedTeam) {
                          addToTeam(player);
                        } else {
                          alert('Please select a team first in the Team Preparation section!');
                        }
                      }}
                      disabled={!!(selectedTeam && (state.preparedTeams[selectedTeam] || []).some((p: Player) => p.id === player.id))}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                        selectedTeam && (state.preparedTeams[selectedTeam] || []).some((p: Player) => p.id === player.id)
                          ? 'bg-green-600 text-white' 
                          : selectedTeam
                            ? 'bg-blue-600 hover:bg-blue-700 text-white'
                            : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {selectedTeam && (state.preparedTeams[selectedTeam] || []).some((p: Player) => p.id === player.id) ? '✓' : '+'}
                    </button>
                    <button
                      onClick={() => {
                        if (selectedTeam) {
                          alert(`Add to target list for ${selectedTeam}`);
                        } else {
                          alert('Please select a team first!');
                        }
                      }}
                      className="px-2 py-1 rounded text-xs font-medium bg-gray-600 hover:bg-gray-700 text-white transition-all"
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
        Showing {filteredPlayers.length} of {state.players.length} players
      </div>
    </div>
  );
};

// Team Insights Analysis
const TeamInsights: React.FC = () => {
  const { state } = useAppContext();
  
  const teamCount = Object.keys(state.preparedTeams).length;
  
  if (teamCount < 2) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 text-center">
        <h2 className="text-2xl font-bold text-cyan-400 mb-4">📊 Team Insights</h2>
        <div className="text-gray-400">
          Prepare at least 2 teams to unlock automatic insights and comparison features
        </div>
      </div>
    );
  }

  const analyzeTeam = (teamName: string, teamPlayers: Player[]) => {
    const batsmen = teamPlayers.filter(p => p.role === 'Batsman').length;
    const bowlers = teamPlayers.filter(p => p.role === 'Bowler').length;
    const allrounders = teamPlayers.filter(p => p.role === 'All-rounder').length;
    const wicketkeepers = teamPlayers.filter(p => p.role === 'Wicket-keeper').length;
    
    const avgStrikeRate = teamPlayers
      .filter(p => p.strikeRate > 0)
      .reduce((sum, p) => sum + p.strikeRate, 0) / 
      Math.max(teamPlayers.filter(p => p.strikeRate > 0).length, 1);
    
    const avgEconomy = teamPlayers
      .filter(p => p.economy > 0)
      .reduce((sum, p) => sum + p.economy, 0) / 
      Math.max(teamPlayers.filter(p => p.economy > 0).length, 1);
    
    const avgWinProb = ((avgStrikeRate / 150) * 40) + ((10 - avgEconomy) * 6);
    const totalSpent = teamPlayers.reduce((sum, p) => sum + p.currentPrice, 0);
    
    return {
      name: teamName,
      players: teamPlayers.length,
      batsmen,
      bowlers,
      allrounders,
      wicketkeepers,
      avgStrikeRate,
      avgEconomy,
      avgWinProb,
      totalSpent,
      budgetUtilization: (totalSpent / 12000) * 100
    };
  };

  const teamAnalyses = Object.entries(state.preparedTeams).map(([teamName, players]) => 
    analyzeTeam(teamName, players as Player[])
  );

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-cyan-400 mb-6">📊 Team Insights & Comparison</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {teamAnalyses.map((analysis, index) => (
          <div key={analysis.name} className="bg-gray-700/50 rounded-lg p-5 border border-gray-600">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-white">{analysis.name}</h3>
              <div className="text-right">
                <div className="text-2xl font-bold text-cyan-400">{analysis.avgWinProb.toFixed(1)}%</div>
                <div className="text-xs text-gray-400">Win Probability</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{analysis.batsmen}</div>
                <div className="text-xs text-gray-400">Batsmen</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{analysis.bowlers}</div>
                <div className="text-xs text-gray-400">Bowlers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{analysis.allrounders}</div>
                <div className="text-xs text-gray-400">All-rounders</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">{analysis.wicketkeepers}</div>
                <div className="text-xs text-gray-400">Wicket-keepers</div>
              </div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-300">Avg Strike Rate:</span>
                <span className="font-medium text-white">{analysis.avgStrikeRate.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Avg Economy:</span>
                <span className="font-medium text-white">{analysis.avgEconomy.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Budget Used:</span>
                <span className="font-medium text-green-400">{analysis.budgetUtilization.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Total Spent:</span>
                <span className="font-medium text-cyan-400">{formatCurrency(analysis.totalSpent)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-gray-700/50 rounded-lg p-5 border border-gray-600">
        <h3 className="text-lg font-bold text-white mb-4">📊 Comparative Analysis</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-600">
                <th className="px-4 py-3 text-left text-cyan-300 font-semibold">Metric</th>
                {teamAnalyses.map(analysis => (
                  <th key={analysis.name} className="px-4 py-3 text-center text-cyan-300 font-semibold">
                    {analysis.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              <tr>
                <td className="px-4 py-3 text-gray-300">Win Probability</td>
                {teamAnalyses.map(analysis => (
                  <td key={analysis.name} className="px-4 py-3 text-center font-medium text-white">
                    <span className="text-lg">{analysis.avgWinProb.toFixed(1)}%</span>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-3 text-gray-300">Batting Strength</td>
                {teamAnalyses.map(analysis => (
                  <td key={analysis.name} className="px-4 py-3 text-center">
                    <div className="text-white font-medium">{analysis.avgStrikeRate.toFixed(1)}</div>
                    <div className="text-xs text-gray-400">{analysis.batsmen} players</div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-3 text-gray-300">Bowling Strength</td>
                {teamAnalyses.map(analysis => (
                  <td key={analysis.name} className="px-4 py-3 text-center">
                    <div className="text-white font-medium">{analysis.avgEconomy.toFixed(2)}</div>
                    <div className="text-xs text-gray-400">{analysis.bowlers} players</div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-3 text-gray-300">Budget Efficiency</td>
                {teamAnalyses.map(analysis => (
                  <td key={analysis.name} className="px-4 py-3 text-center">
                    <div className="text-white font-medium">{analysis.budgetUtilization.toFixed(1)}%</div>
                    <div className="text-xs text-gray-400">{formatCurrency(analysis.totalSpent)}</div>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App: React.FC = () => {
  const { state } = useAppContext();
  
  if (state.isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <div className="text-cyan-400 text-xl font-semibold">Loading IPL Dashboard...</div>
          <div className="text-gray-400 mt-2">Preparing your cricket analytics experience</div>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🏏</div>
          <div className="text-red-400 text-2xl font-bold mb-2">Error Loading Data</div>
          <div className="text-gray-300 mb-6">{state.error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-4">
            2025 Team Builder
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Advanced analytics dashboard for building and comparing IPL teams with 120 crore budget constraints
          </p>
        </header>

        <div className="space-y-8">
          <TeamPreparationSection />
          <PlayerIntelligenceHub />
          <TeamInsights />
        </div>
      </div>
    </div>
  );
};

// Root Component
const RootApp: React.FC = () => {
  return (
    <AppProvider>
      <App />
    </AppProvider>
  );
};

export default RootApp;