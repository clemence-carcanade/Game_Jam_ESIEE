import "./index.css";
import { Composition, Folder } from "remotion";
import { BandeAnnonce } from "./BandeAnnonce";
import { SceneFin } from "./scenes/SceneFin";
import { SceneGameplay } from "./scenes/SceneGameplay";
import { SceneHistoire } from "./scenes/SceneHistoire";
import { SceneIntro } from "./scenes/SceneIntro";

const FPS = 30;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BandeAnnonce"
        component={BandeAnnonce}
        durationInFrames={900}
        fps={FPS}
        width={1280}
        height={720}
      />
      <Folder name="Scenes">
        <Composition
          id="Intro"
          component={SceneIntro}
          durationInFrames={300}
          fps={FPS}
          width={1280}
          height={720}
        />
        <Composition
          id="Histoire"
          component={SceneHistoire}
          durationInFrames={170}
          fps={FPS}
          width={1280}
          height={720}
        />
        <Composition
          id="Gameplay"
          component={SceneGameplay}
          durationInFrames={270}
          fps={FPS}
          width={1280}
          height={720}
        />
        <Composition
          id="Fin"
          component={SceneFin}
          durationInFrames={190}
          fps={FPS}
          width={1280}
          height={720}
        />
      </Folder>
    </>
  );
};
