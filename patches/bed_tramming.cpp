/**
 * PROUI Bed Tramming
 * Author: Miguel A. Risco-Castillo
 * version: 2.2.0
 * Date: 2023/09/07
 *
 * Duender: two coordinate sets —
 *   Manual (fullManualTramming): nozzle at bed-screw edges
 *   Auto / probe wizard: probe-reachable points (CR Touch offset)
 * Front = low Y, Back = high Y. Do not re-home between corners.
 */

#include "../../../inc/MarlinConfigPre.h"

#if ALL(DWIN_LCD_PROUI, LCD_BED_TRAMMING)

#include "../../../core/types.h"
#include "../../../gcode/gcode.h"
#include "../../../module/motion.h"
#include "../../marlinui.h"

#if HAS_MESH || HAS_BED_PROBE
  #include "../../../feature/bedlevel/bedlevel.h"
  #include "../../../module/probe.h"
#endif

#include "bed_tramming.h"
#include "dwin.h"

#if HAS_TRAMMING_WIZARD
  extern bed_mesh_t tram_zmesh;
#endif

// Manual tram — nozzle over leveling screws / bed edges (measured)
#ifndef DUENDER_TRAM_MANUAL_FL
  #define DUENDER_TRAM_MANUAL_FL { 1, 22 }
  #define DUENDER_TRAM_MANUAL_FR { 201, 22 }
  #define DUENDER_TRAM_MANUAL_BR { 201, 235 }
  #define DUENDER_TRAM_MANUAL_BL { 1, 235 }
#endif

// Auto / probe tram — probe tip targets (must stay inside probe reach)
// Reach with offset {-31,-39}: roughly X 10..170, Y 10..196
// FR/BR X201 and back Y230 were nozzle-edge style and go out of bounds for the probe
#ifndef DUENDER_TRAM_PROBE_FL
  #define DUENDER_TRAM_PROBE_FL { 19, 61 }
  #define DUENDER_TRAM_PROBE_FR { 170, 61 }
  #define DUENDER_TRAM_PROBE_BR { 170, 196 }
  #define DUENDER_TRAM_PROBE_BL { 19, 196 }
#endif

bool tram(const uint8_t point OPTARG(HAS_BED_PROBE, bool stow_probe/*=true*/)) {
  const bool manual = TERN1(HAS_BED_PROBE, hmiData.fullManualTramming);

  constexpr xy_pos_t m_fl = DUENDER_TRAM_MANUAL_FL, m_fr = DUENDER_TRAM_MANUAL_FR,
                     m_br = DUENDER_TRAM_MANUAL_BR, m_bl = DUENDER_TRAM_MANUAL_BL;
  #if HAS_BED_PROBE
    constexpr xy_pos_t p_fl = DUENDER_TRAM_PROBE_FL, p_fr = DUENDER_TRAM_PROBE_FR,
                       p_br = DUENDER_TRAM_PROBE_BR, p_bl = DUENDER_TRAM_PROBE_BL;
  #endif

  float x, y;
  switch (point) {
    case LF:
      LCD_MESSAGE(MSG_TRAM_FL);
      x = manual ? m_fl.x : TERN(HAS_BED_PROBE, p_fl.x, m_fl.x);
      y = manual ? m_fl.y : TERN(HAS_BED_PROBE, p_fl.y, m_fl.y);
      break;
    case RF:
      LCD_MESSAGE(MSG_TRAM_FR);
      x = manual ? m_fr.x : TERN(HAS_BED_PROBE, p_fr.x, m_fr.x);
      y = manual ? m_fr.y : TERN(HAS_BED_PROBE, p_fr.y, m_fr.y);
      break;
    case LB:
      LCD_MESSAGE(MSG_TRAM_BL);
      x = manual ? m_bl.x : TERN(HAS_BED_PROBE, p_bl.x, m_bl.x);
      y = manual ? m_bl.y : TERN(HAS_BED_PROBE, p_bl.y, m_bl.y);
      break;
    case RB:
      LCD_MESSAGE(MSG_TRAM_BR);
      x = manual ? m_br.x : TERN(HAS_BED_PROBE, p_br.x, m_br.x);
      y = manual ? m_br.y : TERN(HAS_BED_PROBE, p_br.y, m_br.y);
      break;
    case TRAM_C:
      LCD_MESSAGE(MSG_TRAM_C);
      if (manual) {
        x = (m_fl.x + m_fr.x) * 0.5f;
        y = (m_fl.y + m_bl.y) * 0.5f;
      }
      else {
        #if HAS_BED_PROBE
          x = (p_fl.x + p_fr.x) * 0.5f;
          y = (p_fl.y + p_bl.y) * 0.5f;
        #else
          x = (m_fl.x + m_fr.x) * 0.5f;
          y = (m_fl.y + m_bl.y) * 0.5f;
        #endif
      }
      break;
    default:
      x = m_fl.x;
      y = m_fl.y;
      break;
  }

  ui.set_status(TS(manual ? F("Man X:") : F("Prb X:"), p_float_t(x, 0), F(" Y:"), p_float_t(y, 0)));

  if (!all_axes_homed()) gcode.process_subcommands_now(F("G28"));

  #if HAS_BED_PROBE
    if (manual) {
      TERN_(HAS_LEVELING, set_bed_leveling_enabled(false));
      gcode.process_subcommands_now(MString<120>(
        F("M420S0\nG90\nG0F300Z" STRINGIFY(BED_TRAMMING_Z_HOP) "\nG0F5000X"), x, 'Y', y,
        F("\nG0F300Z" STRINGIFY(BED_TRAMMING_HEIGHT))
      ));
      return false;
    }

    gcode.process_subcommands_now(MString<120>(
      F("M420S0\nG90\nG0F300Z" STRINGIFY(BED_TRAMMING_Z_HOP) "\nG0F5000X"), x, 'Y', y
    ));

    if (!probe.can_reach(x, y)) {
      LCD_MESSAGE(MSG_M48_OUT_OF_BOUNDS);
      return true;
    }

    if (stow_probe) probe.stow();
    const float zval = probe_at_point(x, y, stow_probe);
    TERN_(HAS_TRAMMING_WIZARD, tram_zmesh[point % 2][point / 2] = zval);
    const bool tram_error = isnan(zval);
    if (tram_error) {
      LCD_MESSAGE(MSG_M48_OUT_OF_BOUNDS);
    }
    else {
      ui.set_status(TS(F("X:"), p_float_t(x, 0), F(" Y:"), p_float_t(y, 0), F(" Z:"), p_float_t(zval, 2)));
    }
    return tram_error;
  #else
    gcode.process_subcommands_now(MString<120>(
      F("M420S0\nG90\nG0F300Z" STRINGIFY(BED_TRAMMING_Z_HOP) "\nG0F5000X"), x, 'Y', y,
      F("\nG0F300Z" STRINGIFY(BED_TRAMMING_HEIGHT))
    ));
    return false;
  #endif
}

#endif // DWIN_LCD_PROUI && LCD_BED_TRAMMING
