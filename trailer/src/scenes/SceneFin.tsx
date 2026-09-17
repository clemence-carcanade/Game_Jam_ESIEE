import { Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

// La fin : la video de conclusion (11 s), avec sa propre bande son.
export const SceneFin: React.FC = () => {
  return (
    <AbsoluteFill name="Fin" style={{ backgroundColor: "black" }}>
      <Video
        src={staticFile("fin.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};
