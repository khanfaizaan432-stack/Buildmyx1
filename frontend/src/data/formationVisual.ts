/** Pitch positions for tactics UI (top/left %). Attackers toward top, GK toward bottom — matches real width. */
export type FieldPos = { pos: "GK" | "DF" | "MF" | "FW"; top: number; left: number };

export const FORMATION_FIELD_POSITIONS: Record<string, FieldPos[]> = {
  "4-3-3": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 18 }, { pos: "DF", top: 72, left: 38 }, { pos: "DF", top: 72, left: 62 }, { pos: "DF", top: 72, left: 82 },
    { pos: "MF", top: 50, left: 25 }, { pos: "MF", top: 50, left: 50 }, { pos: "MF", top: 50, left: 75 },
    { pos: "FW", top: 20, left: 20 }, { pos: "FW", top: 14, left: 50 }, { pos: "FW", top: 20, left: 80 },
  ],
  "4-4-2": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 18 }, { pos: "DF", top: 72, left: 38 }, { pos: "DF", top: 72, left: 62 }, { pos: "DF", top: 72, left: 82 },
    { pos: "MF", top: 50, left: 18 }, { pos: "MF", top: 50, left: 38 }, { pos: "MF", top: 50, left: 62 }, { pos: "MF", top: 50, left: 82 },
    { pos: "FW", top: 20, left: 35 }, { pos: "FW", top: 20, left: 65 },
  ],
  "4-2-3-1": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 18 }, { pos: "DF", top: 72, left: 38 }, { pos: "DF", top: 72, left: 62 }, { pos: "DF", top: 72, left: 82 },
    { pos: "MF", top: 58, left: 35 }, { pos: "MF", top: 58, left: 65 },
    { pos: "MF", top: 38, left: 20 }, { pos: "MF", top: 38, left: 50 }, { pos: "MF", top: 38, left: 80 },
    { pos: "FW", top: 14, left: 50 },
  ],
  "3-5-2": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 25 }, { pos: "DF", top: 72, left: 50 }, { pos: "DF", top: 72, left: 75 },
    { pos: "MF", top: 50, left: 12 }, { pos: "MF", top: 50, left: 31 }, { pos: "MF", top: 50, left: 50 }, { pos: "MF", top: 50, left: 69 }, { pos: "MF", top: 50, left: 88 },
    { pos: "FW", top: 20, left: 35 }, { pos: "FW", top: 20, left: 65 },
  ],
  "5-3-2": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 12 }, { pos: "DF", top: 72, left: 31 }, { pos: "DF", top: 72, left: 50 }, { pos: "DF", top: 72, left: 69 }, { pos: "DF", top: 72, left: 88 },
    { pos: "MF", top: 50, left: 25 }, { pos: "MF", top: 50, left: 50 }, { pos: "MF", top: 50, left: 75 },
    { pos: "FW", top: 20, left: 35 }, { pos: "FW", top: 20, left: 65 },
  ],
  "3-4-3": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 25 }, { pos: "DF", top: 72, left: 50 }, { pos: "DF", top: 72, left: 75 },
    { pos: "MF", top: 50, left: 18 }, { pos: "MF", top: 50, left: 38 }, { pos: "MF", top: 50, left: 62 }, { pos: "MF", top: 50, left: 82 },
    { pos: "FW", top: 20, left: 20 }, { pos: "FW", top: 14, left: 50 }, { pos: "FW", top: 20, left: 80 },
  ],
  "4-1-4-1": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 18 }, { pos: "DF", top: 72, left: 38 }, { pos: "DF", top: 72, left: 62 }, { pos: "DF", top: 72, left: 82 },
    { pos: "MF", top: 60, left: 50 },
    { pos: "MF", top: 42, left: 12 }, { pos: "MF", top: 42, left: 37 }, { pos: "MF", top: 42, left: 63 }, { pos: "MF", top: 42, left: 88 },
    { pos: "FW", top: 14, left: 50 },
  ],
  "4-4-1-1": [
    { pos: "GK", top: 88, left: 50 },
    { pos: "DF", top: 72, left: 18 }, { pos: "DF", top: 72, left: 38 }, { pos: "DF", top: 72, left: 62 }, { pos: "DF", top: 72, left: 82 },
    { pos: "MF", top: 50, left: 18 }, { pos: "MF", top: 50, left: 38 }, { pos: "MF", top: 50, left: 62 }, { pos: "MF", top: 50, left: 82 },
    { pos: "FW", top: 28, left: 50 }, { pos: "FW", top: 14, left: 50 },
  ],
};
