/**
 * Party Popper Animation Component
 */
import React, { useEffect, useState } from 'react';
import '../styles/PartyPopper.css';

export function PartyPopper({ x, y, onComplete }) {
  const [poppers, setPoppers] = useState([]);

  useEffect(() => {
    // Generate 15 party poppers with random trajectories
    const newPoppers = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      emoji: '🎉',
      x,
      y,
      angle: (Math.PI * 2 * i) / 15, // Distribute evenly in circle
      velocity: 150 + Math.random() * 100, // Random velocity
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 720, // Random spin
    }));

    setPoppers(newPoppers);

    // Clean up after animation completes
    const timer = setTimeout(() => {
      if (onComplete) onComplete();
    }, 1500);

    return () => clearTimeout(timer);
  }, [x, y, onComplete]);

  return (
    <div className="party-popper-container">
      {poppers.map((popper) => (
        <div
          key={popper.id}
          className="party-popper"
          style={{
            '--start-x': `${popper.x}px`,
            '--start-y': `${popper.y}px`,
            '--angle': `${popper.angle}rad`,
            '--velocity': `${popper.velocity}px`,
            '--rotation': `${popper.rotation}deg`,
            '--rotation-speed': `${popper.rotationSpeed}deg`,
          }}
        >
          {popper.emoji}
        </div>
      ))}
    </div>
  );
}
