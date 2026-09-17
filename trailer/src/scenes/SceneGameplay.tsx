import { Audio } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  Series,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { CartoucheTexte } from "../CartoucheTexte";
import { ChatQuiCourt } from "../ChatQuiCourt";

// Un plan de gameplay : un fond de niveau, le maître, le chat qui court,
// et une phrase d'accroche.
const Plan: React.FC<{
  fond: string;
  perso: string;
  taillePerso: number;
  texte: string;
  son: string;
  cadreSon?: number;
}> = ({ fond, perso, taillePerso, texte, son, cadreSon = 4 }) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Img
        src={staticFile(fond)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          scale: interpolate(frame, [0, 90], [1.12, 1.02]),
        }}
      />
      <AbsoluteFill
        name="Assombrissement"
        style={{ backgroundColor: "rgba(5, 4, 16, 0.28)" }}
      />
      <Img
        src={staticFile(perso)}
        style={{
          position: "absolute",
          right: 60,
          bottom: 40,
          height: taillePerso,
          imageRendering: "pixelated",
          translate: `0px ${Math.round(Math.sin(frame / 6) * 4)}px`,
        }}
      />
      <ChatQuiCourt
        departX={-150}
        arriveeX={720}
        y={500}
        taille={130}
        dureeEnFrames={90}
      />
      <CartoucheTexte
        nom="Accroche"
        texte={texte}
        apparition={8}
        taille={34}
        bas={500}
      />
      <Audio from={cadreSon} src={staticFile(son)} volume={0.8} />
    </AbsoluteFill>
  );
};

// Trois plans rapides : les maîtres, les pièges, le vrai but du jeu.
export const SceneGameplay: React.FC = () => {
  return (
    <AbsoluteFill name="Gameplay">
      <Series>
        <Series.Sequence durationInFrames={90} name="Les maitres">
          <Plan
            fond="fonds/niveau2.png"
            perso="persos/mamie.png"
            taillePerso={300}
            texte="7 maîtres à tester..."
            son="sons/saut.mp3"
          />
        </Series.Sequence>
        <Series.Sequence durationInFrames={90} name="Les pieges">
          <Plan
            fond="fonds/niveau5.png"
            perso="persos/chef_vener.png"
            taillePerso={320}
            texte="des pièges à débusquer..."
            son="sons/boing.mp3"
          />
        </Series.Sequence>
        <Series.Sequence durationInFrames={90} name="Le but">
          <Plan
            fond="fonds/niveau3.png"
            perso="persos/fillette.png"
            taillePerso={310}
            texte={"et un seul but :\nfaire mourir le chat !"}
            son="sons/mort.mp3"
            cadreSon={14}
          />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
