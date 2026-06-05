// Navigation bar — breaks at 390px
function Navbar() {
  const links = [
    { label: "Dashboard", href: "/" },
    { label: "Projects", href: "/projects" },
    { label: "Team Members", href: "/team" },
    { label: "Billing & Plans", href: "/billing" },
    { label: "Settings", href: "/settings" },
    { label: "Help Center", href: "/help" },
  ];

  return (
    <nav className="navbar">
      <div className="nav-brand">WorkspaceHub</div>
      <ul className="nav-links">
        {links.map(link => (
          <li key={link.href}><a href={link.href}>{link.label}</a></li>
        ))}
      </ul>
    </nav>
  );
}

export default Navbar;
