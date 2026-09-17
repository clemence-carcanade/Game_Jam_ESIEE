import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";

// Le chat joueur (planche assets/images/chat.png, ligne de la marche),
// extrait en 8 images jouees a la meme cadence que dans le jeu (0,07 s).
const CADENCE = 30 * 0.07;

export const ChatQuiCourt: React.FC<{
  departX: number;
  arriveeX: number;
  y: number;
  taille?: number;
  dureeEnFrames: number;
}> = ({ departX, arriveeX, y, taille = 128, dureeEnFrames }) => {
  const frame = useCurrentFrame();
  const image = Math.floor(frame / CADENCE) % 8;

  return (
    <Img
      src={staticFile(`chat/marche_${image}.png`)}
      style={{
        position: "absolute",
        width: taille,
        height: taille,
        top: y,
        imageRendering: "pixelated",
        scale: arriveeX < departX ? "-1 1" : "1 1",
        left: interpolate(frame, [0, dureeEnFrames], [departX, arriveeX], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
      }}
    />
  );
};
