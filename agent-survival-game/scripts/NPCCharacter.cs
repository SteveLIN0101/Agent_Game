using Godot;

/// <summary>角色状态枚举——同时用于初始状态设置和编辑器预览</summary>
public enum CharacterVisualState
{
    Normal,
    Hungry,
    Dehydrated,
    Injured,
    Disturbed,
    Sick,
    Terminal
}

/// <summary>
/// 单个 NPC 角色节点——管理隐藏属性（饥饿/口渴/精神）并根据状态刷新精灵。
/// [Tool] 使脚本在编辑器中也运行，贴图配置后实时生效。
/// </summary>
[Tool]
public partial class NPCCharacter : Control
{
    // ── 基础信息 ───────────────────────────────────────────────────────
    [ExportGroup("基础信息")]
    [Export] public string NpcName { get; set; } = "";
    [Export] public string CharacterFileId { get; set; } = "";
    [Export] public string Skill { get; set; } = "";

    // ── 初始状态（编辑器里设置什么，运行时就从什么状态开始）────────────
    [ExportGroup("初始状态")]
    private CharacterVisualState _initialState = CharacterVisualState.Normal;
    [Export]
    public CharacterVisualState InitialState
    {
        get => _initialState;
        set { _initialState = value; DeferredRefresh(); }
    }

    // ── 状态贴图（任一属性被赋值时立即刷新精灵）────────────────────────
    [ExportGroup("状态贴图")]

    private Texture2D _textureNormal = null!;
    [Export] public Texture2D TextureNormal
    {
        get => _textureNormal;
        set { _textureNormal = value; DeferredRefresh(); }
    }

    private Texture2D _textureHungry = null!;
    [Export] public Texture2D TextureHungry
    {
        get => _textureHungry;
        set { _textureHungry = value; DeferredRefresh(); }
    }

    private Texture2D _textureDehydrated = null!;
    [Export] public Texture2D TextureDehydrated
    {
        get => _textureDehydrated;
        set { _textureDehydrated = value; DeferredRefresh(); }
    }

    private Texture2D _textureInjured = null!;
    [Export] public Texture2D TextureInjured
    {
        get => _textureInjured;
        set { _textureInjured = value; DeferredRefresh(); }
    }

    private Texture2D _textureDisturbed = null!;
    [Export] public Texture2D TextureDisturbed
    {
        get => _textureDisturbed;
        set { _textureDisturbed = value; DeferredRefresh(); }
    }

    private Texture2D _textureSick = null!;
    [Export] public Texture2D TextureSick
    {
        get => _textureSick;
        set { _textureSick = value; DeferredRefresh(); }
    }

    private Texture2D _textureTerminal = null!;
    [Export] public Texture2D TextureTerminal
    {
        get => _textureTerminal;
        set { _textureTerminal = value; DeferredRefresh(); }
    }

    // ── 状态图标（可在 Inspector 里为每个状态配置对应图标）────────────
    [ExportGroup("状态图标")]

    private Texture2D _iconBackground = null!;
    [Export] public Texture2D IconBackground
    {
        get => _iconBackground;
        set { _iconBackground = value; DeferredRefresh(); }
    }

    private Texture2D _iconHungry = null!;
    [Export] public Texture2D IconHungry
    {
        get => _iconHungry;
        set { _iconHungry = value; DeferredRefresh(); }
    }

    private Texture2D _iconDehydrated = null!;
    [Export] public Texture2D IconDehydrated
    {
        get => _iconDehydrated;
        set { _iconDehydrated = value; DeferredRefresh(); }
    }

    private Texture2D _iconInjured = null!;
    [Export] public Texture2D IconInjured
    {
        get => _iconInjured;
        set { _iconInjured = value; DeferredRefresh(); }
    }

    private Texture2D _iconDisturbed = null!;
    [Export] public Texture2D IconDisturbed
    {
        get => _iconDisturbed;
        set { _iconDisturbed = value; DeferredRefresh(); }
    }

    private Texture2D _iconSick = null!;
    [Export] public Texture2D IconSick
    {
        get => _iconSick;
        set { _iconSick = value; DeferredRefresh(); }
    }

    private Texture2D _iconTerminal = null!;
    [Export] public Texture2D IconTerminal
    {
        get => _iconTerminal;
        set { _iconTerminal = value; DeferredRefresh(); }
    }

    // ── 隐藏属性（私有，0–100）────────────────────────────────────────
    private int _hunger = 100;
    private int _thirst = 100;
    private int _mental = 100;
    private bool _isDead = false;

    public int Hunger => _hunger;
    public int Thirst => _thirst;
    public int Mental => _mental;
    public bool IsAlive => !_isDead;

    private TextureRect _sprite = null!;
    private Control _statusPanel = null!;
    private TextureRect _panelBg = null!;
    private TextureRect _statusIcon = null!;

    private const string CharBasePath =
        "res://data/red-dust-character-states-en/red-dust-character-states-en/";

    // ── 生命周期 ───────────────────────────────────────────────────────

    public override void _Ready()
    {
        _sprite = GetNode<TextureRect>("Sprite");
        _statusPanel = GetNode<Control>("StatusPanel");
        _panelBg     = GetNode<TextureRect>("StatusPanel/PanelBg");
        _statusIcon  = GetNode<TextureRect>("StatusPanel/StatusIcon");

        // 运行时：把隐藏属性设置成与 InitialState 对应的值
        if (!Engine.IsEditorHint())
            ApplyInitialState();

        RefreshSprite();
    }

    // ── 初始状态 → 隐藏属性 ───────────────────────────────────────────

    /// <summary>根据 InitialState 设置隐藏属性初始值。</summary>
    private void ApplyInitialState()
    {
        (_hunger, _thirst, _mental) = _initialState switch
        {
            CharacterVisualState.Hungry     => (25,  100, 100),
            CharacterVisualState.Dehydrated => (100,  25, 100),
            CharacterVisualState.Injured    => (100,  45, 100),
            CharacterVisualState.Sick       => (100, 100,  45),
            CharacterVisualState.Disturbed  => (100, 100,  25),
            CharacterVisualState.Terminal   => (5,    5,    5),
            _                               => (100, 100, 100),
        };
        _isDead = _initialState == CharacterVisualState.Terminal;
    }

    // ── 公开方法 ───────────────────────────────────────────────────────

    /// <summary>用代码直接设置初始隐藏属性（覆盖 InitialState 枚举）。</summary>
    public void Initialize(int hunger, int thirst, int mental)
    {
        _hunger = Mathf.Clamp(hunger, 0, 100);
        _thirst = Mathf.Clamp(thirst, 0, 100);
        _mental = Mathf.Clamp(mental, 0, 100);
        _isDead = false;
        RefreshSprite();
    }

    public void Kill()
    {
        _isDead = true;
        RefreshSprite();
    }

    public void ModifyHunger(int delta)
    {
        _hunger = Mathf.Clamp(_hunger + delta, 0, 100);
        RefreshSprite();
    }

    public void ModifyThirst(int delta)
    {
        _thirst = Mathf.Clamp(_thirst + delta, 0, 100);
        RefreshSprite();
    }

    public void ModifyMental(int delta)
    {
        _mental = Mathf.Clamp(_mental + delta, 0, 100);
        RefreshSprite();
    }

    // ── 外观状态映射 ──────────────────────────────────────────────────

    public string GetVisualState()
    {
        // 编辑器：直接显示 InitialState（所见即所得）
        if (Engine.IsEditorHint())
        {
            return _initialState switch
            {
                CharacterVisualState.Hungry     => "hungry",
                CharacterVisualState.Dehydrated => "dehydrated",
                CharacterVisualState.Injured    => "injured",
                CharacterVisualState.Disturbed  => "disturbed",
                CharacterVisualState.Sick       => "sick",
                CharacterVisualState.Terminal   => "terminal",
                _                               => "normal",
            };
        }

        // 运行时：根据隐藏属性动态计算
        if (!IsAlive) return "terminal";
        int minStat = Mathf.Min(_hunger, Mathf.Min(_thirst, _mental));
        if (minStat < 15)  return "terminal";
        if (_mental < 30)  return "disturbed";
        if (_thirst < 30)  return "dehydrated";
        if (_hunger < 30)  return "hungry";
        if (_mental < 55)  return "sick";
        if (_thirst < 55)  return "injured";
        if (_hunger < 55)  return "hungry";
        return "normal";
    }

    // ── 精灵刷新 ──────────────────────────────────────────────────────

    public void RefreshSprite()
    {
        if (_sprite == null)
            _sprite = GetNodeOrNull<TextureRect>("Sprite");
        if (_sprite == null) return;

        string state = GetVisualState();

        Texture2D tex = state switch
        {
            "normal"     => _textureNormal,
            "hungry"     => _textureHungry,
            "dehydrated" => _textureDehydrated,
            "injured"    => _textureInjured,
            "disturbed"  => _textureDisturbed,
            "sick"       => _textureSick,
            "terminal"   => _textureTerminal,
            _            => _textureNormal,
        };

        if (tex == null && CharacterFileId != "")
        {
            string path = $"{CharBasePath}{CharacterFileId}-{state}-fullbody.png";
            tex = ResourceLoader.Load<Texture2D>(path);
        }

        _sprite.Texture = tex;

        bool isTerminal = state == "terminal";
        _sprite.Modulate = (!_isDead && !isTerminal)
            ? Colors.White
            : new Color(0.4f, 0.4f, 0.4f, 0.5f);

        RefreshStatusIcons(state);
    }

    // ── 状态图标刷新 ──────────────────────────────────────────────────

    private void RefreshStatusIcons(string state)
    {
        // 懒加载节点（[Tool] 模式下 _Ready 可能还未执行）
        if (_statusPanel == null) _statusPanel = GetNodeOrNull<Control>("StatusPanel");
        if (_statusPanel == null) return;
        if (_panelBg    == null) _panelBg    = GetNodeOrNull<TextureRect>("StatusPanel/PanelBg");
        if (_statusIcon == null) _statusIcon = GetNodeOrNull<TextureRect>("StatusPanel/StatusIcon");

        if (state == "normal")
        {
            _statusPanel.Visible = false;
            return;
        }

        _statusPanel.Visible = true;

        if (_panelBg != null)
            _panelBg.Texture = _iconBackground;

        Texture2D icon = state switch
        {
            "hungry"     => _iconHungry,
            "dehydrated" => _iconDehydrated,
            "injured"    => _iconInjured,
            "disturbed"  => _iconDisturbed,
            "sick"       => _iconSick,
            "terminal"   => _iconTerminal,
            _            => null!,
        };

        if (_statusIcon != null)
            _statusIcon.Texture = icon;
    }

    private void DeferredRefresh()
    {
        if (IsInsideTree())
            CallDeferred(MethodName.RefreshSprite);
    }
}
