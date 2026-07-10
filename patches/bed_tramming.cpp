/**
 * PROUI Bed Tramming
 * Author: Miguel A. Risco-Castillo
 * version: 2.2.0
 * Date: 2023/09/07
 *
 * Duender measured tram corners (absolute). Front = low Y, Back = high Y.
 * Do not re-home between corners.
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

// Measured on hardware — absolute probe/nozzle tram targets
#ifndef DUENDER_TRAM_FL
  #define DUENDER_TRAM_FL { 1, 22 }
  #define DUENDER_TRAM_FR { 201, 22 }
  #define DUENDER_TRAM_BR { 201, 235 }
  #define DUENDER_TRAM_BL { 1, 235 }
#endif

bool tram(const uint8_t point OPTARG(HAS_BED_PROBE, bool stow_probe/*=true*/)) {
  constexpr xy_pos_t fl = DUENDER_TRAM_FL, fr = DUENDER_TRAM_FR,
                     br = DUENDER_TRAM_BR, bl = DUENDER_TRAM_BL;

  float x = fl.x, y = fl.y;
  switch (point) {
    case LF: LCD_MESSAGE(MSG_TRAM_FL); x = fl.x; y = fl.y; break;
    case RF: LCD_MESSAGE(MSG_TRAM_FR); x = fr.x; y = fr.y; break;
    case LB: LCD_MESSAGE(MSG_TRAM_BL); x = bl.x; y = bl.y; break;
    case RB: LCD_MESSAGE(MSG_TRAM_BR); x = br.x; y = br.y; break;
    case TRAM_C: LCD_MESSAGE(MSG_TRAM_C); x = (fl.x + fr.x) * 0.5f; y = (fl.y + bl.y) * 0.5f; break;
  }

  ui.set_status(TS(F("Tram X:"), p_float_t(x, 0), F(" Y:"), p_float_t(y, 0)));

  if (!all_axes_homed()) gcode.process_subcommands_now(F("G28"));

  #if HAS_BED_PROBE
    if (hmiData.fullManualTramming) {
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
