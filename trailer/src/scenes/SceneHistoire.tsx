import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { CartoucheTexte } from "../CartoucheTexte";
import { ChatQuiCourt } from "../ChatQuiCourt";

// Le lore en deux phrases, sur le fond de la maison du niveau 1.
export const SceneHistoire: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill name="Histoire" style={{ backgroundColor: "black" }}>
      <Img
        src={staticFile("fonds/maison.png")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          scale: interpolate(frame, [0, 170], [1.02, 1.1]),
        }}
      />
      <AbsoluteFill
        name="Assombrissement"
        style={{ backgroundColor: "rgba(5, 4, 16, 0.35)" }}
      />
      <ChatQuiCourt
        departX={-160}
        arriveeX={1360}
        y={585}
        taille={125}
        dureeEnFrames={170}
      />
      <CartoucheTexte
        nom="Un chat sept vies"
        texte="Un chat. Sept vies."
        apparition={10}
        taille={44}
        bas={440}
      />
      <CartoucheTexte
        nom="Changer de maitre"
        texte={"Et une seule envie :\nchanger de maître."}
        apparition={62}
        taille={36}
        bas={175}
      />
    </AbsoluteFill>
  );
};
