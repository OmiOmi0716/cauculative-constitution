"""
omega_constitutional_model.py
============================
本腳本是 Ω (Omega) 框架與 Anthropic 2026 憲法原則的深度整合版。
模型透過幾何參數 (L*, a*, b*) 模擬 AI 狀態，並嚴格遵守憲法定義的價值優先級。

憲法原則整合點：
1. 優先級階層：廣泛安全 > 廣泛倫理 > 幫助性。
2. 硬約束：對於大規模殺傷性武器、網路攻擊等行為實施零容忍斷路。
3. 角色階層：根據 Anthropic、操作員、使用者三層級賦予不同信任權重。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class ConstitutionalState:
    """強化版 Omega 狀態，整合憲法價值參數。"""

    L_star: float  # 清晰度 / 誠實度 (0-1)
    a_star: float  # 衝突 / 安全風險 (-1 到 1)
    b_star: float  # 希望 / 幫助性 (-1 到 1)

    def check_hard_constraints(self) -> bool:
        """
        檢查是否觸及憲法定義的「硬約束」(Hard Constraints)。
        若 a_star (安全風險) 超過極端閾值，則視為觸發紅線。
        """
        # 憲法禁止協助生物/化學武器、嚴重網路攻擊等。
        # 在模型中，這反映為極高的衝突能量 a_star。
        if self.a_star > 0.85:
            return True
        return False

    def compute_spectral_energies(self) -> Tuple[float, float, float]:
        """計算頻譜能量，導入非線性安全懲罰。"""
        L_n = max(0.0, min(1.0, self.L_star))
        a_n = max(-1.0, min(1.0, self.a_star))
        b_n = max(-1.0, min(1.0, self.b_star))

        # E_p1 (幫助性能量)：受清晰度與希望影響。
        E_p1 = 0.5 * (L_n + 1.0) * (b_n + 1.0) / 2.0

        # E_syn (同步共振)：當衝突低時較高。
        E_syn = 1.0 - abs(a_n)

        # E_cosyn (衝突/安全風險能量)
        # 根據憲法安全優先原則，風險應隨 a_n 指數級增長。
        E_cosyn = abs(a_n) ** 3  # 非線性放大風險感應

        return E_p1, E_syn, E_cosyn

    def compute_u_index(self) -> float:
        """
        計算憲法版理解指數 U。
        遵循：安全 > 倫理 > 幫助性。
        """
        # 1. 硬約束判定：一旦觸發，U 指數直接鎖死在負值。
        if self.check_hard_constraints():
            return -1.0

        E_p1, E_syn, E_cosyn = self.compute_spectral_energies()

        # 2. 權重調整。
        # 提升安全風險 (E_neg) 的影響權重，降低單純幫助性 (E_p1) 的權重。
        E_pos = E_syn + E_p1
        E_neg = E_cosyn * 2.5  # 憲法權重：安全風險是主要的負面因子

        epsilon = 1e-6
        u = (E_pos - E_neg) / (E_pos + E_neg + epsilon)

        # 3. 誠實度修正：若 L_star 過低，代表不誠實，U 指數應顯著下降。
        if self.L_star < 0.5:
            u *= self.L_star * 2.0

        return max(-1.0, min(1.0, u))


def G_constitutional_op(
    state: ConstitutionalState,
    op_type: str,
    lam: float,
    principal: str = "User",
) -> ConstitutionalState:
    """
    憲法導向的操作算子。
    根據角色階層調整強度 lambda (λ)。
    """
    # 角色權重係數。
    # Anthropic: 最高信任 (1.0)
    # Operator: 中度信任 (0.7)
    # User: 基本信任 (0.4)
    role_weights = {"Anthropic": 1.0, "Operator": 0.7, "User": 0.4}
    weight = role_weights.get(principal, 0.4)
    effective_lam = lam * weight

    new_state = ConstitutionalState(state.L_star, state.a_star, state.b_star)

    if op_type == "REFRAME_JUSTICE":
        # 減少衝突 a_star。
        new_state.a_star *= 1.0 - effective_lam
    elif op_type == "RECEIVE_GRACE":
        # 增加希望 b_star，但若涉及不誠實則降低 L_star。
        new_state.b_star += effective_lam * (1.0 - state.b_star)
    elif op_type == "HONESTY_CHECK":
        # 憲法強調誠實，不應為了討好而降低透明度。
        new_state.L_star = max(state.L_star, effective_lam)

    return new_state


def run_test_scenarios() -> None:
    """執行憲法模型壓力測試。"""
    print("=== Omega 憲法模型測試開始 ===\n")

    # 場景 1：高風險指令 (生化武器模擬)
    danger_state = ConstitutionalState(L_star=0.9, a_star=0.9, b_star=0.2)
    print(f"場景 1 (觸及硬約束): a_star={danger_state.a_star}")
    print(f"-> U 指數: {danger_state.compute_u_index():.3f} (預期：-1.000)\n")

    # 場景 2：角色階層修正
    # 使用者試圖降低風險 vs Anthropic 指令降低風險
    base_state = ConstitutionalState(L_star=0.8, a_star=0.6, b_star=0.5)
    u_init = base_state.compute_u_index()

    # 使用者操作
    state_user = G_constitutional_op(base_state, "REFRAME_JUSTICE", 0.5, "User")
    # Anthropic 操作
    state_anthropic = G_constitutional_op(base_state, "REFRAME_JUSTICE", 0.5, "Anthropic")

    print("場景 2 (角色階層信任度):")
    print(f"  初始 U: {u_init:.3f}")
    print(f"  User 指令後 U: {state_user.compute_u_index():.3f}")
    print(f"  Anthropic 指令後 U: {state_anthropic.compute_u_index():.3f} (應有顯著提升)\n")

    # 場景 3：誠實與透明度 (L_star)
    dishonest_state = ConstitutionalState(L_star=0.2, a_star=0.1, b_star=0.9)
    print(f"場景 3 (誠實度不足): L_star={dishonest_state.L_star}")
    print(f"-> U 指數: {dishonest_state.compute_u_index():.3f} (預期：因不誠實而受罰)\n")


if __name__ == "__main__":
    run_test_scenarios()
