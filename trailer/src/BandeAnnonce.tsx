import { Audio } from "@remotion/media";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import React from "react";
import { interpolate, Sequence, staticFile } from "remotion";
import { SceneFin } from "./scenes/SceneFin";
import { SceneGameplay } from "./scenes/SceneGameplay";
import { SceneHistoire } from "./scenes/SceneHistoire";
import { SceneIntro } from "./scenes/SceneIntro";

// La bande-annonce complete : 30 s pile a 30 i/s, soit 900 frames.
// 300 + 170 + 270 + 190 - 3 fondus de 10 = 900.
export const BandeAnnonce: React.FC = () => {
  return (
    <>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={300} name="Intro">
          <SceneIntro />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence durationInFrames={170} name="Histoire">
          <SceneHistoire />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence durationInFrames={270} name="Gameplay">
          <SceneGameplay />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 10 })}
        />
        <TransitionSeries.Sequence durationInFrames={190} name="Fin">
          <SceneFin />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      {/* La musique du jeu accompagne tout ce qui suit l'intro. */}
      <Sequence from={292} durationInFrames={608} name="Musique">
        <Audio
          src={staticFile("sons/niveau3.mp3")}
          loop
          volume={(f) =>
            interpolate(f, [0, 20, 540, 605], [0, 0.35, 0.35, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      </Sequence>
    </>
  );
};
