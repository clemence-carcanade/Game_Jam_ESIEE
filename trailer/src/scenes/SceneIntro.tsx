import { Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

// La cinematique d'intro du jeu (10 s), avec sa bande son.
export const SceneIntro: React.FC = () => {
  return (
    <AbsoluteFill name="Intro" style={{ backgroundColor: "black" }}>
      <Video
        src={staticFile("intro_logo.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};
