import React from "react";
import { Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { policePixel } from "./polices";

// Un cartouche de texte dans le style de la boite de dialogue de l'intro :
// fond sombre, texte pixel blanc. Apparait en fondu + petite montee.
export const CartoucheTexte: React.FC<{
  nom: string;
  texte: string;
  apparition: number;
  taille?: number;
  bas?: number;
  disparition?: number;
}> = ({ nom, texte, apparition, taille = 40, bas = 70, disparition }) => {
  const frame = useCurrentFrame();
  const finFondu =
    disparition === undefined
      ? [1e9, 1e9 + 1]
      : [disparition, disparition + 12];

  return (
    <Interactive.Div
      name={nom}
      style={{
        position: "absolute",
        bottom: bas,
        left: "50%",
        width: "max-content",
        maxWidth: 1120,
        padding: "26px 42px",
        backgroundColor: "rgba(13, 12, 28, 0.85)",
        border: "3px solid rgba(255, 255, 255, 0.35)",
        borderRadius: 10,
        color: "white",
        fontFamily: policePixel,
        fontSize: taille,
        lineHeight: 1.6,
        textAlign: "center",
        whiteSpace: "pre-line",
        opacity: interpolate(
          frame,
          [apparition, apparition + 12, finFondu[0], finFondu[1]],
          [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        ),
        translate: interpolate(
          frame,
          [apparition, apparition + 14],
          ["-50% 26px", "-50% 0px"],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          },
        ),
      }}
    >
      {texte}
    </Interactive.Div>
  );
};
