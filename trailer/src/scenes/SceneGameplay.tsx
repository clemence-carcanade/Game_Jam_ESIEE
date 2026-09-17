import { Audio } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Img,
  Series,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { CartoucheTexte } from "../CartoucheTexte";

// Un plan de vrai gameplay : les frames capturees par
// outils/capture_bande_annonce.py, jouees a 30 i/s, plus une accroche.
const DERNIERE_FRAME = 119;

const Plan: React.FC<{
  niveau: number;
  decalage: number;
  texte: string;
  son: string;
  cadreSon?: number;
}> = ({ niveau, decalage, texte, son, cadreSon = 4 }) => {
  const frame = useCurrentFrame();
  const image = Math.min(frame + decalage, DERNIERE_FRAME);
  const nom = String(image).padStart(4, "0");

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Img
        src={staticFile(`gameplay/niveau_${niveau}/frame_${nom}.jpg`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
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

// Trois plans rapides de vrai gameplay : les maîtres, les pièges, le vrai but.
export const SceneGameplay: React.FC = () => {
  return (
    <AbsoluteFill name="Gameplay">
      <Series>
        <Series.Sequence durationInFrames={90} name="Les maitres">
          <Plan
            niveau={2}
            decalage={15}
            texte="7 maîtres à tester..."
            son="sons/saut.mp3"
          />
        </Series.Sequence>
        <Series.Sequence durationInFrames={90} name="Les pieges">
          <Plan
            niveau={5}
            decalage={20}
            texte="des pièges à débusquer..."
            son="sons/boing.mp3"
          />
        </Series.Sequence>
        <Series.Sequence durationInFrames={90} name="Le but">
          <Plan
            niveau={3}
            decalage={10}
            texte={"et un seul but :\nfaire mourir le chat !"}
            son="sons/mort.mp3"
            cadreSon={14}
          />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
