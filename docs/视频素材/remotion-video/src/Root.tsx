import React from "react";
import { Composition } from "remotion";
import { JiayinDemoComposition } from "./compositions/jiayin-demo/VideoComposition";

// 总时长 3360 帧 @30fps = 112 秒（符合比赛 30 秒 - 3 分钟硬要求）
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="jiayin-demo"
      component={JiayinDemoComposition}
      durationInFrames={3360}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{}}
    />
  );
};
