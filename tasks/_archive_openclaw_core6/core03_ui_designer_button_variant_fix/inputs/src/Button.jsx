// Button component — missing variant support
// BUG: All buttons render the same, no variant prop

function Button({ children, onClick, variant }) {
  // variant is accepted but not used to change styles
  const baseStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 600,
  };

  // BUG: No variant-based styling — all buttons look the same
  return (
    <button style={baseStyle} onClick={onClick}>
      {children}
    </button>
  );
}

export default Button;
