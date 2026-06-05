using Godot;
using System;

public partial class Fan1 : Sprite2D
{
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	// 在风扇节点的脚本里
	public override void _Process(double delta)
	{
		RotationDegrees += 120f * (float)delta; // 每秒转120度
	}
	
}
