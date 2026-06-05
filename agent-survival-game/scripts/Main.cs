using Godot;
using AgentSurvivalGame;

/// <summary>
/// 主场景脚本——当前阶段：在避难所背景上展示四名角色精灵。
/// </summary>
public partial class Main : Control
{
	// ── 角色节点 ───────────────────────────────────────────────────────
	private NPCCharacter[] _characters = null!;

	// ── 游戏状态 ───────────────────────────────────────────────────────
	private readonly GameState _state = new();

	public override void _Ready()
	{
		_characters = new NPCCharacter[]
		{
			GetNode<NPCCharacter>("CharacterLayer/CharMaDehai"),
			GetNode<NPCCharacter>("CharacterLayer/CharShenZhiyue"),
			GetNode<NPCCharacter>("CharacterLayer/CharXiaoTie"),
			GetNode<NPCCharacter>("CharacterLayer/CharLaoQian"),
		};

		for (int i = 0; i < _state.Npcs.Length && i < _characters.Length; i++)
		{
			NpcState npc = _state.Npcs[i];
			_characters[i].Initialize(npc.InitialHunger, npc.InitialThirst, npc.InitialMental);

			if (!npc.IsAlive)
				_characters[i].Kill();
		}
	}
}
