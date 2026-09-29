import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
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
} from "./components";

// ============ 场景5 · 高难对话彩排室（18s / 540f） ============
export const Scene5Rehearsal: React.FC = () => (
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
      <Kicker text="高难对话彩排室" />
      <Headline lines={["最难开口的话", "先跟 AI 爸妈彩排"]} delay={26} />
      <Chips items={["挂科了", "分手了", "想辞职", "要生活费"]} delay={44} />
      <div style={{ marginTop: 44 }}>
        <PhoneMock shot="shot-rehearsal.png" imgH={1688} frameH={900} delay={50} />
      </div>
      <QuoteCard text="练顺了，再打真电话" delay={130} />
    </AbsoluteFill>
  </SceneFade>
);

// ============ 场景6 · 治愈转折（10s / 300f） ============
export const Scene6Heal: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = interpolate(frame, [0, 150, 300], [0.96, 1.04, 0.98], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ringScale = interpolate(frame % 90, [0, 90], [0.4, 1.6]);
  const ringOpacity = interpolate(frame % 90, [0, 90], [0.5, 0]);
  return (
    <SceneFade durationInFrames={300}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 100% 60% at 50% 45%, #4A2E14 0%, ${BRAND.bgDeep} 70%)`,
        }}
      />
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}
      >
        {/* 电话拨号脉冲 */}
        <div
          style={{
            width: 300,
            height: 300,
            borderRadius: "50%",
            background: "rgba(255,138,76,0.12)",
            border: "3px solid rgba(255,138,76,0.6)",
            transform: `scale(${pulse})`,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: "3px solid rgba(255,138,76,0.5)",
              transform: `scale(${ringScale})`,
              opacity: ringOpacity,
            }}
          />
          <div style={{ fontSize: 120 }}>📞</div>
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 50),
            marginTop: 80,
            fontSize: 64,
            fontWeight: 800,
            color: BRAND.cream,
            textAlign: "center",
            lineHeight: 1.6,
          }}
        >
          说出口的那一刻
          <br />
          <span style={{ color: BRAND.accent }}>电话那头，笑了</span>
        </div>
      </AbsoluteFill>
    </SceneFade>
  );
};

// ============ 场景7 · 功能快剪（20s / 600f，4 个功能 × 5s） ============
const FEATURES: { shot: string; imgH: number; kicker: string; caption: string }[] = [
  { shot: "shot-topic.png", imgH: 1958, kicker: "连心话题卡", caption: "4 场景 × 5 个不尬聊的话题" },
  { shot: "shot-pet.png", imgH: 1724, kicker: "合养小宠物", caption: "全家的孩子，一起养大" },
  { shot: "shot-checkin.png", imgH: 4224, kicker: "每日安心打卡", caption: "让爸妈连续 N 天知道你很好" },
  { shot: "shot-parent.png", imgH: 1688, kicker: "爸妈也爱用", caption: "双角色设计，关心是双向的" },
];

export const Scene7Features: React.FC = () => {
  const frame = useCurrentFrame();
  const seg = 150; // 每功能 5s
  const idx = Math.min(3, Math.floor(frame / seg));
  const local = frame % seg;
  const f = FEATURES[idx];
  return (
    <AbsoluteFill style={{ opacity: interpolate(local, [0, 12, 138, 150], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
      <WarmBg />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          padding: "60px 40px",
        }}
      >
        <Kicker text={f.kicker} delay={0} />
        <div style={{ marginTop: 20 }}>
          <PhoneMock shot={f.shot} imgH={f.imgH} frameH={920} delay={6} />
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 20),
            marginTop: 44,
            fontSize: 46,
            fontWeight: 800,
            color: BRAND.accentSoft,
          }}
        >
          {f.caption}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ============ 场景8 · Slogan 片尾（12s / 360f） ============
export const Scene8Outro: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <SceneFade durationInFrames={360}>
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${BRAND.bgDeep} 0%, #35200E 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          padding: "0 70px",
        }}
      >
        <div
          style={{
            ...fadeSlideUp(frame, 15),
            fontSize: 58,
            fontWeight: 800,
            color: BRAND.cream,
            textAlign: "center",
            lineHeight: 1.8,
          }}
        >
          把养生文<span style={{ color: BRAND.accent }}>翻成关心</span>
          <br />
          把「嗯」<span style={{ color: BRAND.accent }}>翻成「我也想你」</span>
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 100),
            marginTop: 90,
            padding: "26px 60px",
            borderRadius: 999,
            border: `2px solid ${BRAND.accent}`,
            color: BRAND.accentSoft,
            fontSize: 38,
            fontWeight: 800,
            letterSpacing: 8,
          }}
        >
          家音 Jiayin
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 140),
            marginTop: 40,
            fontSize: 34,
            color: BRAND.dim,
            letterSpacing: 3,
          }}
        >
          AI 家庭沟通翻译官
        </div>
        <div
          style={{
            ...fadeSlideUp(frame, 200),
            position: "absolute",
            bottom: 120,
            fontSize: 28,
            color: BRAND.dim,
            textAlign: "center",
            lineHeight: 1.8,
          }}
        >
          2026 iCAN × 快手 · AI 未来创造者挑战赛
          <br />
          「我们与AI」· AI 产品实现方向
        </div>
      </AbsoluteFill>
    </SceneFade>
  );
};
