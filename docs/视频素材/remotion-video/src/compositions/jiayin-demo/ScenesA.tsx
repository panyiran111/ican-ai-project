import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import {
  BRAND,
  SceneFade,
  WarmBg,
  Kicker,
  Headline,
  PhoneMock,
  QuoteCard,
  Chips,
  fadeSlideUp,
  popIn,
} from "./components";

// ============ 场景1 · 痛点开场（8s / 240f） ============
export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const msgs = [
    "妈：这三种食物千万别隔夜吃…",
    "妈：【转发】秋季养生秘诀大全",
    "妈：儿子，妈发的文章你看了没？",
  ];
  return (
    <SceneFade durationInFrames={240}>
      <WarmBg />
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", padding: "0 70px" }}
      >
        {/* 模拟微信消息气泡 */}
        {msgs.map((m, i) => {
          const s = spring({
            frame: frame - (10 + i * 30),
            fps: 30,
            config: { damping: 100, stiffness: 200 },
          });
          // 第三条后被"划走"
          const swiped = frame > 150 && i < 2;
          const swipeX = swiped
            ? interpolate(frame, [150, 180], [0, -900], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
            : 0;
          return (
            <div
              key={i}
              style={{
                transform: `translateX(${swipeX}px) scale(${Math.min(1, s)})`,
                opacity: Math.min(1, s * 1.5) * (swiped ? 0.25 : 1),
                alignSelf: "flex-start",
                maxWidth: 760,
                marginBottom: 34,
                padding: "28px 38px",
                borderRadius: "8px 28px 28px 28px",
                background: "#F5F0E8",
                color: "#2A2018",
                fontSize: 40,
                fontWeight: 600,
                lineHeight: 1.4,
                boxShadow: "0 16px 40px rgba(0,0,0,0.4)",
              }}
            >
              {m}
            </div>
          );
        })}
        <div
          style={{
            ...fadeSlideUp(frame, 170),
            marginTop: 50,
            fontSize: 52,
            fontWeight: 800,
            color: BRAND.cream,
            textAlign: "center",
            lineHeight: 1.5,
          }}
        >
          爸妈发的养生文
          <br />
          <span style={{ color: BRAND.accent }}>你也是这样划走的吗？</span>
        </div>
      </AbsoluteFill>
    </SceneFade>
  );
};

// ============ 场景2 · 产品亮相（9s / 270f） ============
export const Scene2Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 100, stiffness: 160 },
  });
  const glow = interpolate(frame, [30, 270], [0.5, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <SceneFade durationInFrames={270}>
      <WarmBg />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          padding: "0 60px",
        }}
      >
        {/* Logo 光环 */}
        <div
          style={{
            width: 320,
            height: 320,
            borderRadius: "50%",
            border: `3px solid rgba(255,138,76,${0.35 * glow})`,
            boxShadow: `0 0 ${120 * glow}px rgba(255,138,76,${0.35 * glow})`,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            transform: `scale(${logoScale})`,
            marginBottom: 60,
          }}
        >
          <div style={{ fontSize: 150, fontWeight: 900, color: BRAND.cream }}>家</div>
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 40),
            fontSize: 110,
            fontWeight: 900,
            color: BRAND.cream,
            letterSpacing: 14,
          }}
        >
          家音
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 60),
            fontSize: 34,
            color: BRAND.dim,
            letterSpacing: 10,
            marginTop: 14,
          }}
        >
          J I A Y I N
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 90),
            marginTop: 56,
            fontSize: 56,
            fontWeight: 800,
            color: BRAND.accentSoft,
            letterSpacing: 4,
          }}
        >
          AI 家庭沟通翻译官
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 130),
            marginTop: 44,
            fontSize: 42,
            color: BRAND.cream,
            opacity: 0.85,
            textAlign: "center",
            lineHeight: 1.7,
          }}
        >
          爸妈的每一条养生文
          <br />
          都是没说出口的想你
        </div>
      </AbsoluteFill>
    </SceneFade>
  );
};

// ============ 场景3 · 关心解码器（18s / 540f） ============
export const Scene3Decode: React.FC = () => (
  <SceneFade durationInFrames={540}>
    <WarmBg />
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        padding: "60px 40px",
      }}
    >
      <Kicker text="关心解码器" />
      <Headline lines={["60 秒养生文", "翻译成一句想你"]} delay={26} />
      <div style={{ marginTop: 50 }}>
        <PhoneMock shot="shot-decode.png" imgH={1970} frameH={980} />
      </div>
      <QuoteCard text="这不是养生文，是想你回家吃饭" delay={110} />
    </AbsoluteFill>
  </SceneFade>
);

// ============ 场景4 · 回音壁（17s / 510f） ============
export const Scene4Reply: React.FC = () => (
  <SceneFade durationInFrames={510}>
    <WarmBg />
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        padding: "60px 40px",
      }}
    >
      <Kicker text="回音壁" />
      <Headline lines={["把敷衍", "换成他们想听的话"]} delay={26} />
      <Chips items={["嘴硬", "标准", "撒娇"]} delay={44} />
      <div style={{ marginTop: 44 }}>
        <PhoneMock shot="shot-reply.png" imgH={2566} frameH={980} delay={50} />
      </div>
      <QuoteCard text="像你本人说的话，一键复制" delay={130} />
    </AbsoluteFill>
  </SceneFade>
);
