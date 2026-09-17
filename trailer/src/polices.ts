import { loadFont } from "@remotion/google-fonts/PressStart2P";

// Police pixel proche de celle du jeu, mais avec les accents français.
export const { fontFamily: policePixel } = loadFont("normal", {
  weights: ["400"],
  subsets: ["latin", "latin-ext"],
});
