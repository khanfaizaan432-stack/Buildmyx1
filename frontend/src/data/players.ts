export interface Player {
  id: number;
  name: string;
  squad: string;
  nation: string;
  pos: string;
  sub_position: string;
  quality_final: number;
  fit_gegenpress: number;
  fit_high_press: number;
  fit_tiki_taka: number;
  fit_counter_attack: number;
  fit_park_the_bus: number;
  fit_long_ball: number;
  fit_high_line: number;
  fit_false_9: number;
  final_value: number;
}

export const MOCK_PLAYERS: Player[] = [
  { id: 1, name: "Alisson", squad: "Liverpool", nation: "Brazil", pos: "GK", sub_position: "Traditional Keeper", quality_final: 0.91, fit_gegenpress: 0.85, fit_high_press: 0.88, fit_tiki_taka: 0.7, fit_counter_attack: 0.75, fit_park_the_bus: 0.8, fit_long_ball: 0.65, fit_high_line: 0.78, fit_false_9: 0.55, final_value: 60 },
  { id: 2, name: "Ederson", squad: "Man City", nation: "Brazil", pos: "GK", sub_position: "Sweeper Keeper", quality_final: 0.89, fit_gegenpress: 0.8, fit_high_press: 0.82, fit_tiki_taka: 0.88, fit_counter_attack: 0.72, fit_park_the_bus: 0.65, fit_long_ball: 0.6, fit_high_line: 0.85, fit_false_9: 0.5, final_value: 55 },
  { id: 3, name: "Virgil van Dijk", squad: "Liverpool", nation: "Netherlands", pos: "DF", sub_position: "Stopper", quality_final: 0.93, fit_gegenpress: 0.9, fit_high_press: 0.87, fit_tiki_taka: 0.75, fit_counter_attack: 0.8, fit_park_the_bus: 0.85, fit_long_ball: 0.78, fit_high_line: 0.88, fit_false_9: 0.4, final_value: 75 },
  { id: 4, name: "Trent Alexander-Arnold", squad: "Liverpool", nation: "England", pos: "DF", sub_position: "Inverted Fullback", quality_final: 0.9, fit_gegenpress: 0.88, fit_high_press: 0.85, fit_tiki_taka: 0.82, fit_counter_attack: 0.78, fit_park_the_bus: 0.6, fit_long_ball: 0.7, fit_high_line: 0.8, fit_false_9: 0.45, final_value: 80 },
  { id: 5, name: "Ruben Dias", squad: "Man City", nation: "Portugal", pos: "DF", sub_position: "Ball-Playing Defender", quality_final: 0.91, fit_gegenpress: 0.85, fit_high_press: 0.83, fit_tiki_taka: 0.88, fit_counter_attack: 0.75, fit_park_the_bus: 0.8, fit_long_ball: 0.65, fit_high_line: 0.87, fit_false_9: 0.42, final_value: 70 },
  { id: 6, name: "Theo Hernandez", squad: "AC Milan", nation: "France", pos: "DF", sub_position: "Wing-Back", quality_final: 0.87, fit_gegenpress: 0.83, fit_high_press: 0.8, fit_tiki_taka: 0.75, fit_counter_attack: 0.85, fit_park_the_bus: 0.55, fit_long_ball: 0.68, fit_high_line: 0.78, fit_false_9: 0.4, final_value: 65 },
  { id: 7, name: "Kevin De Bruyne", squad: "Man City", nation: "Belgium", pos: "MF", sub_position: "Box-to-Box MF", quality_final: 0.95, fit_gegenpress: 0.9, fit_high_press: 0.87, fit_tiki_taka: 0.92, fit_counter_attack: 0.85, fit_park_the_bus: 0.6, fit_long_ball: 0.75, fit_high_line: 0.88, fit_false_9: 0.55, final_value: 100 },
  { id: 8, name: "Pedri", squad: "Barcelona", nation: "Spain", pos: "MF", sub_position: "Advanced Playmaker", quality_final: 0.92, fit_gegenpress: 0.88, fit_high_press: 0.85, fit_tiki_taka: 0.95, fit_counter_attack: 0.78, fit_park_the_bus: 0.55, fit_long_ball: 0.6, fit_high_line: 0.85, fit_false_9: 0.65, final_value: 120 },
  { id: 9, name: "Martin Odegaard", squad: "Arsenal", nation: "Norway", pos: "MF", sub_position: "Advanced Playmaker", quality_final: 0.89, fit_gegenpress: 0.87, fit_high_press: 0.84, fit_tiki_taka: 0.9, fit_counter_attack: 0.8, fit_park_the_bus: 0.58, fit_long_ball: 0.62, fit_high_line: 0.83, fit_false_9: 0.6, final_value: 90 },
  { id: 10, name: "Nicolas Barella", squad: "Inter Milan", nation: "Italy", pos: "MF", sub_position: "Box-to-Box MF", quality_final: 0.88, fit_gegenpress: 0.92, fit_high_press: 0.89, fit_tiki_taka: 0.82, fit_counter_attack: 0.85, fit_park_the_bus: 0.65, fit_long_ball: 0.72, fit_high_line: 0.8, fit_false_9: 0.48, final_value: 85 },
  { id: 11, name: "Erling Haaland", squad: "Man City", nation: "Norway", pos: "FW", sub_position: "Target Man", quality_final: 0.97, fit_gegenpress: 0.88, fit_high_press: 0.85, fit_tiki_taka: 0.75, fit_counter_attack: 0.92, fit_park_the_bus: 0.6, fit_long_ball: 0.88, fit_high_line: 0.82, fit_false_9: 0.45, final_value: 180 },
  { id: 12, name: "Kylian Mbappe", squad: "Real Madrid", nation: "France", pos: "FW", sub_position: "Pressing Forward", quality_final: 0.96, fit_gegenpress: 0.9, fit_high_press: 0.88, fit_tiki_taka: 0.82, fit_counter_attack: 0.95, fit_park_the_bus: 0.55, fit_long_ball: 0.75, fit_high_line: 0.85, fit_false_9: 0.6, final_value: 200 },
  { id: 13, name: "Bukayo Saka", squad: "Arsenal", nation: "England", pos: "FW", sub_position: "Inside Forward", quality_final: 0.91, fit_gegenpress: 0.88, fit_high_press: 0.86, fit_tiki_taka: 0.85, fit_counter_attack: 0.88, fit_park_the_bus: 0.6, fit_long_ball: 0.7, fit_high_line: 0.82, fit_false_9: 0.62, final_value: 150 },
  { id: 14, name: "Lamine Yamal", squad: "Barcelona", nation: "Spain", pos: "FW", sub_position: "Inverted Winger", quality_final: 0.9, fit_gegenpress: 0.86, fit_high_press: 0.83, fit_tiki_taka: 0.92, fit_counter_attack: 0.85, fit_park_the_bus: 0.5, fit_long_ball: 0.6, fit_high_line: 0.82, fit_false_9: 0.7, final_value: 160 },
  { id: 15, name: "Vinicius Jr", squad: "Real Madrid", nation: "Brazil", pos: "FW", sub_position: "Inverted Winger", quality_final: 0.94, fit_gegenpress: 0.88, fit_high_press: 0.85, fit_tiki_taka: 0.82, fit_counter_attack: 0.93, fit_park_the_bus: 0.52, fit_long_ball: 0.68, fit_high_line: 0.82, fit_false_9: 0.62, final_value: 180 },
  { id: 16, name: "Rodrygo", squad: "Real Madrid", nation: "Brazil", pos: "FW", sub_position: "Inside Forward", quality_final: 0.88, fit_gegenpress: 0.85, fit_high_press: 0.82, fit_tiki_taka: 0.85, fit_counter_attack: 0.88, fit_park_the_bus: 0.55, fit_long_ball: 0.65, fit_high_line: 0.8, fit_false_9: 0.68, final_value: 120 },
  { id: 17, name: "Jamal Musiala", squad: "Bayern Munich", nation: "Germany", pos: "MF", sub_position: "Mezzala", quality_final: 0.92, fit_gegenpress: 0.9, fit_high_press: 0.88, fit_tiki_taka: 0.9, fit_counter_attack: 0.85, fit_park_the_bus: 0.55, fit_long_ball: 0.65, fit_high_line: 0.87, fit_false_9: 0.72, final_value: 150 },
  { id: 18, name: "Mohamed Salah", squad: "Liverpool", nation: "Egypt", pos: "FW", sub_position: "Inside Forward", quality_final: 0.93, fit_gegenpress: 0.9, fit_high_press: 0.88, fit_tiki_taka: 0.82, fit_counter_attack: 0.92, fit_park_the_bus: 0.58, fit_long_ball: 0.72, fit_high_line: 0.85, fit_false_9: 0.62, final_value: 120 },
  { id: 19, name: "Rafael Leao", squad: "AC Milan", nation: "Portugal", pos: "FW", sub_position: "Inverted Winger", quality_final: 0.88, fit_gegenpress: 0.84, fit_high_press: 0.82, fit_tiki_taka: 0.8, fit_counter_attack: 0.91, fit_park_the_bus: 0.55, fit_long_ball: 0.7, fit_high_line: 0.78, fit_false_9: 0.55, final_value: 100 },
  { id: 20, name: "Lautaro Martinez", squad: "Inter Milan", nation: "Argentina", pos: "FW", sub_position: "Pressing Forward", quality_final: 0.91, fit_gegenpress: 0.9, fit_high_press: 0.88, fit_tiki_taka: 0.82, fit_counter_attack: 0.88, fit_park_the_bus: 0.65, fit_long_ball: 0.78, fit_high_line: 0.8, fit_false_9: 0.52, final_value: 110 },
  { id: 21, name: "Bruno Fernandes", squad: "Man United", nation: "Portugal", pos: "MF", sub_position: "Advanced Playmaker", quality_final: 0.87, fit_gegenpress: 0.84, fit_high_press: 0.82, fit_tiki_taka: 0.88, fit_counter_attack: 0.82, fit_park_the_bus: 0.6, fit_long_ball: 0.68, fit_high_line: 0.8, fit_false_9: 0.65, final_value: 75 },
  { id: 22, name: "Marcus Rashford", squad: "Man United", nation: "England", pos: "FW", sub_position: "Pressing Forward", quality_final: 0.82, fit_gegenpress: 0.85, fit_high_press: 0.83, fit_tiki_taka: 0.75, fit_counter_attack: 0.9, fit_park_the_bus: 0.55, fit_long_ball: 0.72, fit_high_line: 0.78, fit_false_9: 0.52, final_value: 70 },
  { id: 23, name: "Leroy Sane", squad: "Bayern Munich", nation: "Germany", pos: "FW", sub_position: "Inverted Winger", quality_final: 0.86, fit_gegenpress: 0.85, fit_high_press: 0.83, fit_tiki_taka: 0.85, fit_counter_attack: 0.88, fit_park_the_bus: 0.55, fit_long_ball: 0.65, fit_high_line: 0.82, fit_false_9: 0.58, final_value: 65 },
  { id: 24, name: "William Saliba", squad: "Arsenal", nation: "France", pos: "DF", sub_position: "Ball-Playing Defender", quality_final: 0.89, fit_gegenpress: 0.86, fit_high_press: 0.84, fit_tiki_taka: 0.82, fit_counter_attack: 0.78, fit_park_the_bus: 0.82, fit_long_ball: 0.72, fit_high_line: 0.85, fit_false_9: 0.42, final_value: 80 },
  { id: 25, name: "Joshua Kimmich", squad: "Bayern Munich", nation: "Germany", pos: "MF", sub_position: "Deep Lying Playmaker", quality_final: 0.91, fit_gegenpress: 0.88, fit_high_press: 0.85, fit_tiki_taka: 0.9, fit_counter_attack: 0.8, fit_park_the_bus: 0.68, fit_long_ball: 0.72, fit_high_line: 0.87, fit_false_9: 0.55, final_value: 90 },
];

export const SYNERGY_PAIRS: [string, string][] = [
  ["Trent Alexander-Arnold", "Mohamed Salah"],
  ["Virgil van Dijk", "Alisson"],
  ["Lamine Yamal", "Pedri"],
  ["Kylian Mbappe", "Rodrygo"],
  ["Erling Haaland", "Kevin De Bruyne"],
  ["Bukayo Saka", "Martin Odegaard"],
  ["Rafael Leao", "Theo Hernandez"],
  ["Lautaro Martinez", "Nicolas Barella"],
  ["Leroy Sane", "Jamal Musiala"],
  ["Marcus Rashford", "Bruno Fernandes"],
];

export const TACTIC_BEATS: Record<string, string> = {
  Gegenpress: "Park the Bus",
  "Counter Attack": "High Press",
  "Tiki-Taka": "Long Ball",
  "High Press": "Long Ball",
  "High Line": "Park the Bus",
};

export const FORMATIONS: Record<string, { GK: number; DF: number; MF: number; FW: number }> = {
  "4-3-3":   { GK: 1, DF: 4, MF: 3, FW: 3 },
  "4-2-3-1": { GK: 1, DF: 4, MF: 5, FW: 1 },
  "3-5-2":   { GK: 1, DF: 3, MF: 5, FW: 2 },
  "4-4-2":   { GK: 1, DF: 4, MF: 4, FW: 2 },
  "5-3-2":   { GK: 1, DF: 5, MF: 3, FW: 2 },
  "3-4-3":   { GK: 1, DF: 3, MF: 4, FW: 3 },
  "4-1-4-1": { GK: 1, DF: 4, MF: 5, FW: 1 },
  "4-4-1-1": { GK: 1, DF: 4, MF: 4, FW: 2 },
};

export const TACTICS = [
  "Gegenpress", "High Press", "Tiki-Taka", "Counter Attack",
  "Park the Bus", "Long Ball", "High Line", "False 9",
] as const;

export type TacticName = (typeof TACTICS)[number];

export const TACTIC_COL: Record<TacticName, keyof Player> = {
  Gegenpress: "fit_gegenpress",
  "High Press": "fit_high_press",
  "Tiki-Taka": "fit_tiki_taka",
  "Counter Attack": "fit_counter_attack",
  "Park the Bus": "fit_park_the_bus",
  "Long Ball": "fit_long_ball",
  "High Line": "fit_high_line",
  "False 9": "fit_false_9",
};

export const TACTIC_DESCRIPTIONS: Record<TacticName, string> = {
  Gegenpress: "Win the ball back immediately after losing it",
  "High Press": "Press high up the pitch to force errors",
  "Tiki-Taka": "Short passing and movement to dominate possession",
  "Counter Attack": "Absorb pressure and strike on the break",
  "Park the Bus": "Deep defensive block, hard to break down",
  "Long Ball": "Direct play over the top to target forwards",
  "High Line": "Push the defensive line high to compress space",
  "False 9": "No traditional striker, fluid attacking movement",
};
