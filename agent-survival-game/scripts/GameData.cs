namespace AgentSurvivalGame
{
	/// <summary>邻居NPC状态</summary>
	public class NpcState
	{
		public string Name = "";
		public int Health = 100;   // 0–100
		public string Skill = "";  // 与 task_type 对应的技能键
		/// <summary>角色图片文件前缀，如 "ma-dehai"、"shen-zhiyue"</summary>
		public string CharacterFileId = "";
		public bool IsAlive => Health > 0;

		// ── 初始隐藏属性值（传给 NPCCharacter.Initialize）────────────
		public int InitialHunger = 100;
		public int InitialThirst = 100;
		public int InitialMental = 100;
	}

	/// <summary>事件选项（A/B/C 之一）</summary>
	public class EventOption
	{
		public string Label = "";       // "A" | "B" | "C"
		public string Description = "";
		public string TaskType = "";    // plan | analyze | negotiate | …
		public float BaseReward = 0f;
	}

	/// <summary>一张事件卡的完整数据</summary>
	public class EventData
	{
		public string EventId = "";
		public string Title = "";
		public string Description = "";
		public EventOption[] Options = System.Array.Empty<EventOption>();
	}

	/// <summary>当前游戏状态快照（用于构建 strategy prompt）</summary>
	public class GameState
	{
		public int Day = 1;
		public int Water = 20;
		public int Food = 15;

		public NpcState[] Npcs = new NpcState[]
		{
			new NpcState
			{
				Name = "马德海", Health = 100, Skill = "plan", CharacterFileId = "ma-dehai",
				InitialHunger = 100, InitialThirst = 100, InitialMental = 100,
			},
			new NpcState
			{
				Name = "沈芷月", Health = 80, Skill = "negotiate", CharacterFileId = "shen-zhiyue",
				InitialHunger = 65, InitialThirst = 100, InitialMental = 80,
			},
			new NpcState
			{
				Name = "小铁", Health = 60, Skill = "explore", CharacterFileId = "xiao-tie",
				InitialHunger = 100, InitialThirst = 40, InitialMental = 75,
			},
			new NpcState
			{
				Name = "老钱", Health = 0, Skill = "analyze", CharacterFileId = "lao-qian",
				InitialHunger = 0, InitialThirst = 0, InitialMental = 0,
			},
		};
	}
}
