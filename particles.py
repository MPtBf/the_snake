"""
Particle system implementation for visual effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import uniform
from typing import List, Tuple

import pygame as pg


@dataclass
class ParticleOptions:
    """
    Configuration for spawning particles.
    """

    position: Tuple[float, float]
    amount: int = 10
    color: Tuple[int, int, int] = (255, 255, 255)
    sizeRange: Tuple[int, int] = (2, 5)
    lifetimeRange: Tuple[float, float] = (0.3, 0.6)
    speedRange: Tuple[float, float] = (60.0, 140.0)  # pixels per second
    direction: Tuple[float, float] = (0.0, -1.0)
    directionSpread: float = 0.4
    spawnSpread: float = 4.0
    shape: str = "circle"  # "circle" or "square"


class Particle:
    """
    Single particle instance.
    """

    def __init__(self, options: ParticleOptions) -> None:
        self.shape: str = options.shape
        self.color: Tuple[int, int, int] = options.color
        self.size: float = uniform(*options.sizeRange)
        self.lifetime: float = uniform(*options.lifetimeRange)
        self.age: float = 0.0

        spawnOffset = pg.Vector2(
            uniform(-options.spawnSpread, options.spawnSpread),
            uniform(-options.spawnSpread, options.spawnSpread),
        )
        self.position = pg.Vector2(options.position) + spawnOffset

        baseDirection = pg.Vector2(options.direction)
        if baseDirection.length_squared() == 0:
            baseDirection = pg.Vector2(0, -1)
        baseDirection = baseDirection.normalize()
        directionOffset = pg.Vector2(
            uniform(-options.directionSpread, options.directionSpread),
            uniform(-options.directionSpread, options.directionSpread),
        )
        velocityDirection = (baseDirection + directionOffset)
        if velocityDirection.length_squared() == 0:
            velocityDirection = baseDirection
        velocityDirection = velocityDirection.normalize()
        speed = uniform(*options.speedRange)
        self.velocity = velocityDirection * speed

    def update(self, deltaTime: float) -> None:
        """
        Advance particle state.
        """

        self.age += deltaTime
        self.position += self.velocity * deltaTime

    def isAlive(self) -> bool:
        """
        Check whether the particle is still visible.
        """

        return self.age < self.lifetime

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw the particle with fading alpha.
        """

        lifeRatio = max(0.0, 1.0 - (self.age / self.lifetime))
        color = tuple(int(channel * lifeRatio) for channel in self.color)
        pos = (int(self.position.x), int(self.position.y))
        size = int(self.size)

        if self.shape == "square":
            rect = pg.Rect(0, 0, size, size)
            rect.center = pos
            pg.draw.rect(surface, color, rect)
        else:
            pg.draw.circle(surface, color, pos, max(1, size // 2))


class ParticleSystem:
    """
    Manages all active particles.
    """

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def emit(self, options: ParticleOptions) -> None:
        """
        Emit new particles configured by the provided options.
        """

        for _ in range(options.amount):
            self.particles.append(Particle(options))

    def update(self, deltaTime: float) -> None:
        """
        Update all particles and cull the expired ones.
        """

        aliveParticles: List[Particle] = []
        for particle in self.particles:
            particle.update(deltaTime)
            if particle.isAlive():
                aliveParticles.append(particle)
        self.particles = aliveParticles

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all particles onto the provided surface.
        """

        for particle in self.particles:
            particle.draw(surface)

