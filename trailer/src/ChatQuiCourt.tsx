import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";

// Les 8 images du cycle de course, jouees a 12 images/seconde comme dans le jeu.
const CADENCE = 30 / 12;

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
      src={staticFile(`chats/course_${image}.png`)}
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
