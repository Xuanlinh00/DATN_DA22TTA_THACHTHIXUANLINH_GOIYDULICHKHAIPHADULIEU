---
name: Ethereal Wanderer
colors:
  surface: '#fff7fa'
  surface-dim: '#e2d7dd'
  surface-bright: '#fff7fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fcf1f7'
  surface-container: '#f6ebf1'
  surface-container-high: '#f0e5eb'
  surface-container-highest: '#eae0e6'
  on-surface: '#1f1a1e'
  on-surface-variant: '#544249'
  inverse-surface: '#342f33'
  inverse-on-surface: '#f9eef4'
  outline: '#87717a'
  outline-variant: '#dac0c9'
  surface-tint: '#a43073'
  primary: '#a43073'
  on-primary: '#ffffff'
  primary-container: '#f472b6'
  on-primary-container: '#6d0047'
  inverse-primary: '#ffafd3'
  secondary: '#765469'
  on-secondary: '#ffffff'
  secondary-container: '#fdd0ea'
  on-secondary-container: '#79576c'
  tertiary: '#aa304f'
  on-tertiary: '#ffffff'
  tertiary-container: '#fe708d'
  on-tertiary-container: '#710029'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd8e7'
  primary-fixed-dim: '#ffafd3'
  on-primary-fixed: '#3d0026'
  on-primary-fixed-variant: '#85145a'
  secondary-fixed: '#ffd8ed'
  secondary-fixed-dim: '#e5bad3'
  on-secondary-fixed: '#2c1325'
  on-secondary-fixed-variant: '#5c3d51'
  tertiary-fixed: '#ffd9dd'
  tertiary-fixed-dim: '#ffb2bd'
  on-tertiary-fixed: '#400014'
  on-tertiary-fixed-variant: '#8a1538'
  background: '#fff7fa'
  on-background: '#1f1a1e'
  surface-variant: '#eae0e6'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 64px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 40px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.1em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 40px
  asymmetric-gap-lg: 80px
  asymmetric-gap-sm: 24px
  gutter: 24px
---

## Brand & Style

The design system embodies a "Dreamy Aesthetic" tailored for high-end travel and lifestyle curation. It moves away from rigid structures toward a creative, unique layout that feels fluid and organic. The visual direction is a fusion of **Minimalism** and **Glassmorphism**, prioritizing breathtaking imagery and vast negative space to evoke a sense of calm and exclusivity.

The emotional response should be one of "effortless luxury"—sophisticated but welcoming, modern but poetic. By utilizing translucent layers and soft, sweeping shapes, the interface mimics the diffused light of a Mediterranean sunset or a high-end boutique hotel.

## Colors

The palette is anchored in a monochromatic spectrum of pinks, transitioning from the near-white of a morning sky to the deep, authoritative rose of a vintage wine label.

- **Primary (#f472b6):** Used for key actions and vibrant highlights.
- **Secondary (#fbcfe8):** Applied to soft backgrounds and decorative elements.
- **Neutral/Surface (#fdf2f8):** The foundational canvas, providing a warm alternative to clinical white.
- **Accent/Text (#881337):** A deep rose used for high-contrast typography and critical semantic cues, ensuring readability without resorting to harsh blacks.

Backgrounds should frequently use subtle gradients between the Neutral and Secondary tones to create a sense of depth and movement.

## Typography

This design system employs a high-contrast typographic pairing to signal luxury. **Playfair Display** provides an editorial, authoritative voice for headlines, utilizing its elegant serifs to anchor the page. **Inter** provides a clean, functional counterpoint for body text and navigation, ensuring maximum legibility across all devices.

To maintain the high-end travel feel:
- Use `display-lg` sparingly for hero sections.
- Apply `label-caps` to category tags and small navigation elements to create an "organized luxury" feel.
- Increase line-height on body text to 1.6 to enhance the airy, breathable quality of the layout.

## Layout & Spacing

The layout philosophy rejects perfect symmetry in favor of a **Creative & Unique** rhythm. Use a 12-column grid as a guide, but intentionally offset elements to create a more dynamic, editorial flow.

- **Asymmetry:** Content blocks should vary in their horizontal alignment. For example, a headline might be left-aligned with a 40px margin, while the corresponding body text is tucked into a 2-column offset to the right.
- **Vertical Rhythm:** Use generous, varying white space (e.g., 120px vs 80px) between sections to prevent the UI from feeling "templated."
- **Mobile Reflow:** On mobile, revert to a more standard centered or left-aligned single column, but maintain the large `container-padding` to keep the content feeling premium and uncrowded.

## Elevation & Depth

Depth is achieved through **Glassmorphism** rather than traditional drop shadows. Surfaces should feel like semi-transparent frosted glass, allowing the soft pink background hues or photography to bleed through.

- **Backdrop Blur:** Use a consistent `blur(20px)` on all elevated cards and navigation bars.
- **Tints:** Glass layers should have a white fill at 60-80% opacity.
- **Inner Borders:** Apply a 1px solid white border at 30% opacity to the top and left edges of glass elements to simulate a light-catching "beveled" edge.
- **Shadows:** When shadows are necessary for focus, use "Ambient Rose Shadows"—low opacity (#881337 at 5%) with a very large spread (40px+) to create a soft glow rather than a hard lift.

## Shapes

The shape language is defined by extreme softness. All primary containers, buttons, and image masks must use a minimum radius of **32px**. 

- **Cards & Sections:** Use `rounded-xl` (3rem / 48px) to create a "contained cloud" effect.
- **Interactive Elements:** Buttons and input fields should be fully pill-shaped.
- **Image Treatment:** Images should never have sharp corners. Use the same 32px+ radius, or occasionally use organic, slightly irregular "blob" masks for a more avant-garde travel-log feel.

## Components

### Buttons
Primary buttons are pill-shaped with a solid #f472b6 fill and white text. Secondary buttons utilize the glassmorphism style: a translucent white background with a #881337 border and text.

### Cards
Cards are the hero of this system. They must feature a `backdrop-filter: blur()`, a 32px border radius, and ample internal padding (32px or 40px). Ensure the typography inside cards maintains the asymmetric alignment found in the main layout.

### Input Fields
Inputs should be soft pink (#fbcfe8 at 20% opacity) with a focus state that transitions to a solid 1px #f472b6 border. The height should be generous (min 56px) to maintain the "high-end" tactile feel.

### Chips & Tags
Use the `label-caps` typography. Chips should be small, pill-shaped, and use the #fdf2f8 neutral background with #881337 text to ensure they are legible but not distracting from the main imagery.

### Navigation
The navigation bar should be a floating glass "island" with a high backdrop-blur, centered at the top or bottom of the screen with a significant margin from the edge, reinforcing the "Unique Layout" narrative.