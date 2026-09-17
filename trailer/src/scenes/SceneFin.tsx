import { Audio } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { policePixel } from "../polices";

// Le carton final : le logo du jeu, puis la signature de la jam.
export const SceneFin: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Fin"
      style={{
        backgroundColor: "#0b0a14",
        justifyContent: "center",
        alignItems: "center",
        gap: 70,
      }}
    >
      <Img
        src={staticFile("chatvamal_logo.png")}
        style={{
          width: 700,
          imageRendering: "pixelated",
          scale: interpolate(frame, [4, 26], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.34, 1.56, 0.64, 1),
            output: "perceptual-scale",
          }),
        }}
      />
      <Interactive.Div
        name="Se reincarner"
        style={{
          fontFamily: policePixel,
          fontSize: 30,
          color: "#e8e4d8",
          opacity: interpolate(frame, [45, 60], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Prêt à griller vos vies ?
      </Interactive.Div>
      <Interactive.Div
        name="Signature jam"
        style={{
          fontFamily: policePixel,
          fontSize: 20,
          color: "#8f8aa8",
          opacity: interpolate(frame, [70, 85], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Game Jam ESIEE — 2026
      </Interactive.Div>
      <AbsoluteFill
        name="Fondu final"
        style={{
          backgroundColor: "black",
          pointerEvents: "none",
          opacity: interpolate(frame, [165, 189], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
      <Audio src={staticFile("sons/reincarnation.mp3")} volume={0.8} />
    </AbsoluteFill>
  );
};
