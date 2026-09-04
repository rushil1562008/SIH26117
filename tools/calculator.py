import math
from typing import Dict, Any

class EngineeringCalculator:
    """Deterministic engineering calculation engine to eliminate arithmetic hallucinations."""

    def calculate_pump_efficiency(self, flow_m3h: float, head_m: float, power_kw: float, fluid_density: float = 1000.0) -> Dict[str, Any]:
        """
        Calculates hydraulic power and pump efficiency.
        Formula:
        Flow (m3/s) = Flow (m3/h) / 3600
        Hydraulic Power (kW) = (Density * g * Flow * Head) / 1000
        Efficiency (%) = (Hydraulic Power / Shaft Power) * 100
        """
        g = 9.81
        flow_m3s = flow_m3h / 3600.0
        hydraulic_power_kw = (fluid_density * g * flow_m3s * head_m) / 1000.0
        efficiency_pct = (hydraulic_power_kw / power_kw) * 100.0 if power_kw > 0 else 0.0

        steps = (
            f"=== DETERMINISTIC ENGINEERING CALCULATION STEPS ===\n"
            f"1. Input Parameters:\n"
            f"   - Flow Rate (Q)      : {flow_m3h} m³/h\n"
            f"   - Differential Head (H): {head_m} m\n"
            f"   - Shaft Power (P_in) : {power_kw} kW\n"
            f"   - Fluid Density (ρ)  : {fluid_density} kg/m³\n"
            f"   - Gravity (g)        : {g} m/s²\n\n"
            f"2. Unit Conversion:\n"
            f"   - Q = {flow_m3h} / 3600 = {flow_m3s:.6f} m³/s\n\n"
            f"3. Hydraulic Power Formula:\n"
            f"   - P_hyd = (ρ × g × Q × H) / 1000\n"
            f"   - P_hyd = ({fluid_density} × {g} × {flow_m3s:.6f} × {head_m}) / 1000\n"
            f"   - P_hyd = {hydraulic_power_kw:.2f} kW\n\n"
            f"4. Efficiency Formula:\n"
            f"   - Efficiency = (P_hyd / P_in) × 100\n"
            f"   - Efficiency = ({hydraulic_power_kw:.2f} / {power_kw}) × 100\n"
            f"   - Efficiency = {efficiency_pct:.2f}%\n"
            f"=================================================="
        )

        return {
            "flow_m3h": flow_m3h,
            "head_m": head_m,
            "power_kw": power_kw,
            "hydraulic_power_kw": round(hydraulic_power_kw, 2),
            "efficiency_pct": round(efficiency_pct, 2),
            "calculation_steps": steps,
        }

calculator = EngineeringCalculator()
