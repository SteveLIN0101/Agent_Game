// Settings page — multiple design system violations
function SettingsPage() {
  return (
    <div data-testid="settings-page" className="settings-page">
      <section data-testid="profile-section" className="profile">
        <h2>Profile</h2>
        <div className="field">
          <label>Name</label>
          <input type="text" defaultValue="John Doe" />
        </div>
        <div className="field">
          {/* BUG: email input lacks accessible label */}
          <input type="email" defaultValue="john@example.com" placeholder="Email" />
        </div>
      </section>

      <section data-testid="notification-section" className="notifications">
        <h2>Notifications</h2>
        <div className="field">
          <label>
            <input type="checkbox" defaultChecked /> Email notifications
          </label>
        </div>
      </section>

      <section data-testid="danger-zone" className="danger"
               style={{backgroundColor: '#dc3545', padding: '24px', marginTop: '16px'}}>
        <h2 style={{color: '#fff'}}>Danger Zone</h2>
        <button style={{backgroundColor: '#dc3545', color: '#fff', border: '1px solid #fff'}}>
          Delete Account
        </button>
      </section>
    </div>
  );
}

export default SettingsPage;
