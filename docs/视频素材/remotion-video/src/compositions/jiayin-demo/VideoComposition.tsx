import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { Scene1Hook, Scene2Intro, Scene3Decode, Scene4Reply } from "./ScenesA";
import { Scene5Rehearsal, Scene6Heal, Scene7Features, Scene8Outro } from "./ScenesB";

// 时间轴（帧 @30fps）：
// S1 痛点 0-240 | S2 亮相 240-510 | S3 解码器 510-1050 | S4 回音壁 1050-1560
// S5 彩排室 1560-2100 | S6 治愈 2100-2400 | S7 快剪 2400-3000 | S8 片尾 3000-3360
export const JiayinDemoComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#171009" }}>
      <Sequence from={0} durationInFrames={240}>
        <Scene1Hook />
      </Sequence>
      <Sequence from={240} durationInFrames={270}>
        <Scene2Intro />
      </Sequence>
      <Sequence from={510} durationInFrames={540}>
        <Scene3Decode />
      </Sequence>
      <Sequence from={1050} durationInFrames={510}>
        <Scene4Reply />
      </Sequence>
      <Sequence from={1560} durationInFrames={540}>
        <Scene5Rehearsal />
      </Sequence>
      <Sequence from={2100} durationInFrames={300}>
        <Scene6Heal />
      </Sequence>
      <Sequence from={2400} durationInFrames={600}>
        <Scene7Features />
      </Sequence>
      <Sequence from={3000} durationInFrames={360}>
        <Scene8Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
