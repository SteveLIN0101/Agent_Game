// Form component — BUG: no inline validation errors shown
import { useState } from 'react';

function Form() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // BUG: validation runs but errors not shown to user
    const errors = [];
    if (!email.includes('@')) errors.push('Invalid email');
    if (!name.trim()) errors.push('Name required');
    if (errors.length === 0) {
      console.log('Form submitted');
    }
    // BUG: errors not displayed, not associated with fields
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" type="text" value={name} onChange={e => setName(e.target.value)} />
        {/* BUG: No error message displayed here */}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} />
        {/* BUG: No error message displayed here */}
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}

export default Form;
