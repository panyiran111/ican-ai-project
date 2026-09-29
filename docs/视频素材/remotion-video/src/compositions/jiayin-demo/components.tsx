import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

// ============ 可编辑常量（改文案/配色只动这里） ============
export const BRAND = {
  bgDeep: "#171009",
  bgWarm: "#241608",
  accent: "#FF8A4C",
  accentSoft: "#FFC894",
  cream: "#FFF6EC",
  dim: "#B8A48E",
  cardBg: "rgba(255, 220, 180, 0.08)",
  quoteBg: "rgba(255, 138, 76, 0.14)",
  font: '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif',
};

// 图片原始宽度均为 780px
const SRC_W = 780;

// ============ 通用动画工具 ============
export const fadeSlideUp = (frame: number, start: number, duration = 20) => ({
  opacity: interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }),
  transform: `translateY(${interpolate(frame, [start, start + duration + 5], [36, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })}px)`,
});

export const popIn = (frame: number, fps: number, start: number) =>
  spring({ frame: frame - start, fps, config: { damping: 100, stiffness: 200 } });

// 场景淡入淡出包装（跨场景柔和过渡）
export const SceneFade: React.FC<{ durationInFrames: number; children: React.ReactNode }> = ({
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const fade = interpolate(
    frame,
    [0, 18, durationInFrames - 18, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  return <AbsoluteFill style={{ opacity: fade }}>{children}</AbsoluteFill>;
};

// 暖色背景（深色电影感 + 中央暖光晕）
export const WarmBg: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 120% 70% at 50% 30%, ${BRAND.bgWarm} 0%, ${BRAND.bgDeep} 62%)`,
    }}
  />
);

// 模块小标签（kicker）
export const Kicker: React.FC<{ text: string; delay?: number }> = ({ text, delay = 8 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        ...fadeSlideUp(frame, delay),
        display: "inline-block",
        padding: "14px 36px",
        borderRadius: 999,
        border: `2px solid ${BRAND.accent}`,
        color: BRAND.accentSoft,
        fontSize: 34,
        fontWeight: 700,
        letterSpacing: 6,
        marginBottom: 28,
      }}
    >
      {text}
    </div>
  );
};

// 大标题
export const Headline: React.FC<{ lines: string[]; delay?: number; size?: number }> = ({
  lines,
  delay = 20,
  size = 64,
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ textAlign: "center" }}>
      {lines.map((line, i) => (
        <div
          key={i}
          style={{
            ...fadeSlideUp(frame, delay + i * 12),
            fontSize: size,
            fontWeight: 800,
            color: BRAND.cream,
            lineHeight: 1.35,
            letterSpacing: 2,
          }}
        >
          {line}
        </div>
      ))}
    </div>
  );
};

// ============ 手机壳 + 长图滚动 ============
export const PhoneMock: React.FC<{
  shot: string; // assets 文件名
  imgH: number; // 原始像素高
  frameH?: number; // 可视高度
  scrollFrom?: number; // 滚动起点（0=顶部）
  delay?: number;
}> = ({ shot, imgH, frameH = 1000, scrollFrom = 0, delay = 30 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = popIn(frame, fps, delay);
  const W = 760; // 显示宽度
  const scale = W / SRC_W; // ≈0.974
  const dispH = imgH * scale;
  const maxScroll = Math.max(0, dispH - frameH);

  // 缓动滚动：从 scrollFrom 位置滚到底（或回顶部），30% 时间缓入缓出
  const p = interpolate(frame, [delay + 20, delay + 20 + 200], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t * (3 - 2 * t),
  });
  const scrollY = interpolate(p, [0, 1], [scrollFrom * maxScroll, maxScroll]);

  return (
    <div
      style={{
        transform: `scale(${0.86 + 0.14 * appear}) translateY(${(1 - appear) * 40}px)`,
        opacity: Math.min(1, appear * 1.4),
        width: W + 24,
        borderRadius: 44,
        padding: 12,
        background: "linear-gradient(160deg, #3A2A1C, #20150D)",
        boxShadow: `0 40px 90px rgba(0,0,0,0.65), 0 0 80px rgba(255,138,76,0.15)`,
      }}
    >
      <div
        style={{
          width: W,
          height: frameH,
          borderRadius: 34,
          overflow: "hidden",
          position: "relative",
          background: "#000",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: W,
            transform: `translateY(${-scrollY}px)`,
          }}
        >
          <Img src={staticFile(`assets/${shot}`)} style={{ width: W, display: "block" }} />
        </div>
        {/* 底部渐隐，暗示可滚动 */}
        <div
          style={{
            position: "absolute",
            left: 0,
            bottom: 0,
            width: "100%",
            height: 120,
            background: "linear-gradient(transparent, rgba(0,0,0,0.45))",
          }}
        />
      </div>
    </div>
  );
};

// 底部点题金句卡
export const QuoteCard: React.FC<{ text: string; delay?: number }> = ({ text, delay = 60 }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        ...fadeSlideUp(frame, delay),
        marginTop: 36,
        padding: "30px 48px",
        borderRadius: 28,
        background: BRAND.quoteBg,
        border: `2px solid rgba(255,138,76,0.45)`,
        color: BRAND.accentSoft,
        fontSize: 44,
        fontWeight: 800,
        letterSpacing: 1,
      }}
    >
      {text}
    </div>
  );
};

// 功能标签 chips（逐个弹出）
export const Chips: React.FC<{ items: string[]; delay?: number }> = ({ items, delay = 40 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        display: "flex",
        gap: 20,
        flexWrap: "wrap",
        justifyContent: "center",
        marginTop: 30,
      }}
    >
      {items.map((item, i) => {
        const s = spring({
          frame: frame - (delay + i * 10),
          fps,
          config: { damping: 100, stiffness: 200 },
        });
        return (
          <div
            key={i}
            style={{
              transform: `scale(${s})`,
              opacity: Math.min(1, s * 1.6),
              padding: "16px 30px",
              borderRadius: 20,
              background: BRAND.cardBg,
              border: `2px solid rgba(255,200,148,0.35)`,
              color: BRAND.cream,
              fontSize: 36,
              fontWeight: 700,
            }}
          >
            {item}
          </div>
        );
      })}
    </div>
  );
};
